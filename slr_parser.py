class Grammar:
    def __init__(self, grammar_text):
        self.productions = []
        self.non_terminals = set()
        self.terminals = set()
        self.start_symbol = None
        self.augmented = False
        self.parse_grammar(grammar_text)

    def parse_grammar(self, grammar_text):
        lines = grammar_text.strip().split('\n')
        for i, line in enumerate(lines):
            line = line.strip()
            if not line or line.startswith('#'):
                continue
                
            parts = line.split('->')
            if len(parts) != 2:
                raise ValueError(f"Invalid production format in line {i+1}: {line}")
            
            lhs = parts[0].strip()
            rhs_parts = parts[1].strip().split('|')
            
            self.non_terminals.add(lhs)
            if i == 0 and not self.start_symbol:
                self.start_symbol = lhs
            
            for rhs in rhs_parts:
                rhs = rhs.strip()
                if rhs == 'ε' or rhs == 'epsilon':
                    rhs = ''
                
                self.productions.append((lhs, rhs))
                
                # Extract terminals and non-terminals from RHS
                for symbol in rhs.split():
                    if not symbol:
                        continue
                    if not (symbol[0].isupper() or symbol == '$'):
                        self.terminals.add(symbol)
                    else:
                        self.non_terminals.add(symbol)

    def augment_grammar(self):
        if not self.augmented:
            new_start = f"{self.start_symbol}'"
            while new_start in self.non_terminals:
                new_start += "'"
            
            self.productions.insert(0, (new_start, self.start_symbol))
            self.non_terminals.add(new_start)
            self.start_symbol = new_start
            self.augmented = True
        
        return self

    def get_productions_for(self, non_terminal):
        return [(lhs, rhs) for lhs, rhs in self.productions if lhs == non_terminal]

    def __str__(self):
        result = []
        for lhs in sorted(self.non_terminals):
            rhs_list = [rhs for nt, rhs in self.productions if nt == lhs]
            rhs_str = " | ".join([r if r else "ε" for r in rhs_list])
            result.append(f"{lhs} -> {rhs_str}")
        return "\n".join(result)


class Item:
    def __init__(self, lhs, rhs, dot_position=0, lookahead=None):
        self.lhs = lhs
        self.rhs = rhs
        self.dot_position = dot_position
        self.lookahead = lookahead  # Not used in SLR but kept for future expansion to LR(1)

    def get_next_symbol(self):
        if self.dot_position < len(self.rhs.split()):
            symbols = self.rhs.split()
            return symbols[self.dot_position]
        return None

    def advance_dot(self):
        if self.dot_position < len(self.rhs.split()):
            return Item(self.lhs, self.rhs, self.dot_position + 1, self.lookahead)
        return None

    def __eq__(self, other):
        if not isinstance(other, Item):
            return False
        return (self.lhs == other.lhs and 
                self.rhs == other.rhs and 
                self.dot_position == other.dot_position and 
                self.lookahead == other.lookahead)

    def __hash__(self):
        return hash((self.lhs, self.rhs, self.dot_position, self.lookahead))

    def __str__(self):
        symbols = self.rhs.split()
        if not symbols:  # ε production
            return f"[{self.lhs} -> • {'ε' if not self.rhs else self.rhs}]"
        
        result = f"[{self.lhs} -> "
        for i, symbol in enumerate(symbols):
            if i == self.dot_position:
                result += "• "
            result += symbol + " "
        
        if self.dot_position == len(symbols):
            result += "•"
        
        result += "]"
        return result


class ItemSet:
    def __init__(self, items=None):
        self.items = set(items) if items else set()
        self.transitions = {}  # symbol -> ItemSet index
        self.index = None  # To be set when added to a collection

    def add_item(self, item):
        self.items.add(item)

    def __eq__(self, other):
        if not isinstance(other, ItemSet):
            return False
        return self.items == other.items

    def __hash__(self):
        return hash(frozenset(self.items))

    def __str__(self):
        return f"I{self.index}:\n" + "\n".join(sorted(str(item) for item in self.items))


class SLRParser:
    def __init__(self, grammar_text):
        self.grammar = Grammar(grammar_text)
        self.grammar.augment_grammar()
        self.terminals = self.grammar.terminals
        self.non_terminals = self.grammar.non_terminals
        self.productions = self.grammar.productions
        
        # Add the end-marker $ to terminals
        self.terminals.add('$')
        
        self.first_sets = {}
        self.follow_sets = {}
        self.canonical_collection = []
        self.parsing_table = {}
        
        # Compute FIRST and FOLLOW sets
        self.compute_first_sets()
        self.compute_follow_sets()
        
        # Construct the canonical collection of LR(0) item sets
        self.construct_canonical_collection()
        
        # Build the SLR parsing table
        self.build_parsing_table()

    def compute_first_sets(self):
        # Initialize FIRST sets
        for terminal in self.terminals:
            self.first_sets[terminal] = {terminal}
            
        for non_terminal in self.non_terminals:
            self.first_sets[non_terminal] = set()
        
        # Compute FIRST sets iteratively
        changed = True
        while changed:
            changed = False
            
            for lhs, rhs in self.productions:
                if not rhs:  # ε production
                    if 'ε' not in self.first_sets[lhs]:
                        self.first_sets[lhs].add('ε')
                        changed = True
                else:
                    rhs_symbols = rhs.split()
                    # Add FIRST of the first symbol that can't derive ε
                    all_derive_epsilon = True
                    
                    for symbol in rhs_symbols:
                        # Add all non-ε symbols from FIRST(symbol) to FIRST(lhs)
                        first_of_symbol = {s for s in self.first_sets[symbol] if s != 'ε'}
                        if len(self.first_sets[lhs] | first_of_symbol) > len(self.first_sets[lhs]):
                            self.first_sets[lhs] |= first_of_symbol
                            changed = True
                        
                        # If this symbol can't derive ε, no need to look further
                        if 'ε' not in self.first_sets[symbol]:
                            all_derive_epsilon = False
                            break
                    
                    # If all symbols in RHS can derive ε, add ε to FIRST(lhs)
                    if all_derive_epsilon and rhs_symbols:
                        if 'ε' not in self.first_sets[lhs]:
                            self.first_sets[lhs].add('ε')
                            changed = True

    def compute_follow_sets(self):
        # Initialize FOLLOW sets
        for non_terminal in self.non_terminals:
            self.follow_sets[non_terminal] = set()
        
        # Add $ to FOLLOW of start symbol
        self.follow_sets[self.grammar.start_symbol].add('$')
        
        # Compute FOLLOW sets iteratively
        changed = True
        while changed:
            changed = False
            
            for lhs, rhs in self.productions:
                if not rhs:  # Skip ε productions
                    continue
                    
                rhs_symbols = rhs.split()
                
                # For each symbol B in A -> αBβ
                for i, symbol in enumerate(rhs_symbols):
                    # Only consider non-terminals
                    if symbol not in self.non_terminals:
                        continue
                    
                    # Compute first of everything after B
                    rest = rhs_symbols[i+1:]
                    if not rest:  # B is at the end
                        # Add FOLLOW(A) to FOLLOW(B)
                        if len(self.follow_sets[symbol] | self.follow_sets[lhs]) > len(self.follow_sets[symbol]):
                            self.follow_sets[symbol] |= self.follow_sets[lhs]
                            changed = True
                    else:
                        # Compute FIRST(rest)
                        first_of_rest = set()
                        all_derive_epsilon = True
                        
                        for rest_symbol in rest:
                            # Add all non-ε symbols from FIRST(rest_symbol)
                            first_of_rest |= {s for s in self.first_sets[rest_symbol] if s != 'ε'}
                            
                            # If this symbol can't derive ε, we're done
                            if 'ε' not in self.first_sets[rest_symbol]:
                                all_derive_epsilon = False
                                break
                        
                        # Add FIRST(rest) to FOLLOW(B)
                        if len(self.follow_sets[symbol] | first_of_rest) > len(self.follow_sets[symbol]):
                            self.follow_sets[symbol] |= first_of_rest
                            changed = True
                        
                        # If all symbols in rest can derive ε, add FOLLOW(A) to FOLLOW(B)
                        if all_derive_epsilon:
                            if len(self.follow_sets[symbol] | self.follow_sets[lhs]) > len(self.follow_sets[symbol]):
                                self.follow_sets[symbol] |= self.follow_sets[lhs]
                                changed = True

    def closure(self, item_set):
        result = ItemSet(item_set.items.copy())
        
        changed = True
        while changed:
            changed = False
            new_items = set()
            
            for item in result.items:
                # Get the symbol after the dot
                next_symbol = item.get_next_symbol()
                
                # If the symbol after the dot is a non-terminal
                if next_symbol in self.non_terminals:
                    # Add all productions of this non-terminal
                    for lhs, rhs in self.grammar.get_productions_for(next_symbol):
                        new_item = Item(lhs, rhs, 0)
                        if new_item not in result.items:
                            new_items.add(new_item)
                            changed = True
            
            result.items.update(new_items)
        
        return result

    def goto(self, item_set, symbol):
        new_items = set()
        
        for item in item_set.items:
            # If the next symbol matches the given symbol
            if item.get_next_symbol() == symbol:
                # Advance the dot and add to the new set
                new_item = item.advance_dot()
                if new_item:
                    new_items.add(new_item)
        
        # If there are any new items, compute closure
        if new_items:
            return self.closure(ItemSet(new_items))
        
        return None

    def construct_canonical_collection(self):
        # Start with the closure of {[S' -> •S]}
        start_production = next((p for p in self.productions if p[0] == self.grammar.start_symbol), None)
        if not start_production:
            raise ValueError("Augmented grammar is missing the start production")
        
        initial_item = Item(start_production[0], start_production[1])
        initial_set = self.closure(ItemSet({initial_item}))
        
        self.canonical_collection = [initial_set]
        initial_set.index = 0
        
        # Process all item sets and find their transitions
        processed = 0
        while processed < len(self.canonical_collection):
            current_set = self.canonical_collection[processed]
            
            # Find all possible symbols after dots
            symbols = set()
            for item in current_set.items:
                next_symbol = item.get_next_symbol()
                if next_symbol:
                    symbols.add(next_symbol)
            
            # Compute GOTO for each symbol
            for symbol in symbols:
                goto_set = self.goto(current_set, symbol)
                
                if goto_set:
                    # Check if this set already exists
                    exists = False
                    for i, existing_set in enumerate(self.canonical_collection):
                        if goto_set == existing_set:
                            current_set.transitions[symbol] = i
                            exists = True
                            break
                    
                    # If not, add it to the collection
                    if not exists:
                        goto_set.index = len(self.canonical_collection)
                        self.canonical_collection.append(goto_set)
                        current_set.transitions[symbol] = goto_set.index
            
            processed += 1

    def build_parsing_table(self):
        # Initialize the parsing table
        for i in range(len(self.canonical_collection)):
            self.parsing_table[i] = {
                'action': {t: '' for t in self.terminals},
                'goto': {nt: '' for nt in self.non_terminals if nt != self.grammar.start_symbol}
            }
        
        # Build the action part of the parsing table
        for i, item_set in enumerate(self.canonical_collection):
            for item in item_set.items:
                # Case 1: [A -> α•aβ] - Shift
                next_symbol = item.get_next_symbol()
                if next_symbol in self.terminals and next_symbol in item_set.transitions:
                    next_state = item_set.transitions[next_symbol]
                    action = f"s{next_state}"
                    
                    # Check for conflicts
                    if self.parsing_table[i]['action'][next_symbol] and self.parsing_table[i]['action'][next_symbol] != action:
                        print(f"Shift-Reduce conflict at state {i} for symbol {next_symbol}: "
                              f"{self.parsing_table[i]['action'][next_symbol]} vs {action}")
                    
                    self.parsing_table[i]['action'][next_symbol] = action
                
                # Case 2: [A -> α•] - Reduce
                elif item.dot_position == len(item.rhs.split()) if item.rhs else True:
                    # Don't reduce for the augmented start production
                    if item.lhs == self.grammar.start_symbol and not item.rhs.split():
                        continue
                    
                    # Find the production number
                    prod_num = self.productions.index((item.lhs, item.rhs))
                    
                    # Add reduce actions for each terminal in FOLLOW(A)
                    for terminal in self.follow_sets[item.lhs]:
                        action = f"r{prod_num}"
                        
                        # Check for conflicts
                        if self.parsing_table[i]['action'][terminal] and self.parsing_table[i]['action'][terminal] != action:
                            print(f"Reduce-Reduce conflict at state {i} for symbol {terminal}: "
                                  f"{self.parsing_table[i]['action'][terminal]} vs {action}")
                        
                        self.parsing_table[i]['action'][terminal] = action
                
                # Case 3: [S' -> S•] - Accept
                elif (item.lhs == self.grammar.start_symbol and 
                      item.rhs.split() == [self.grammar.productions[0][1]] and
                      item.dot_position == 1):
                    self.parsing_table[i]['action']['$'] = "acc"
            
            # Fill in the goto part of the parsing table
            for non_terminal in self.non_terminals:
                if non_terminal != self.grammar.start_symbol and non_terminal in item_set.transitions:
                    self.parsing_table[i]['goto'][non_terminal] = item_set.transitions[non_terminal]

    def get_parsing_table_html(self):
        """Returns the parsing table as an HTML table for display"""
        terminals = sorted(self.terminals)
        non_terminals = sorted([nt for nt in self.non_terminals if nt != self.grammar.start_symbol])
        
        html = '<table class="parsing-table">'
        
        # Header row
        html += '<tr><th>State</th>'
        for terminal in terminals:
            html += f'<th>{terminal}</th>'
        for non_terminal in non_terminals:
            html += f'<th>{non_terminal}</th>'
        html += '</tr>'
        
        # Data rows
        for state in range(len(self.canonical_collection)):
            html += f'<tr><td>{state}</td>'
            
            # Action columns
            for terminal in terminals:
                html += f'<td>{self.parsing_table[state]["action"].get(terminal, "")}</td>'
            
            # Goto columns
            for non_terminal in non_terminals:
                html += f'<td>{self.parsing_table[state]["goto"].get(non_terminal, "")}</td>'
            
            html += '</tr>'
        
        html += '</table>'
        return html

    def get_canonical_collection_html(self):
        """Returns the canonical collection as HTML for display"""
        html = '<div class="canonical-collection">'
        
        for i, item_set in enumerate(self.canonical_collection):
            html += f'<div class="item-set"><h3>I{i}:</h3><ul>'
            
            for item in sorted(item_set.items, key=str):
                html += f'<li>{str(item)}</li>'
            
            html += '</ul></div>'
        
        html += '</div>'
        return html

    def get_first_follow_sets_html(self):
        """Returns the FIRST and FOLLOW sets as HTML for display"""
        html = '<div class="sets-container">'
        
        # FIRST sets
        html += '<div class="first-sets"><h3>FIRST Sets:</h3><ul>'
        for symbol in sorted(self.first_sets.keys()):
            first_set = ', '.join(sorted(self.first_sets[symbol])) or 'ø'
            html += f'<li>FIRST({symbol}) = {{{first_set}}}</li>'
        html += '</ul></div>'
        
        # FOLLOW sets
        html += '<div class="follow-sets"><h3>FOLLOW Sets:</h3><ul>'
        for nt in sorted(self.follow_sets.keys()):
            follow_set = ', '.join(sorted(self.follow_sets[nt])) or 'ø'
            html += f'<li>FOLLOW({nt}) = {{{follow_set}}}</li>'
        html += '</ul></div>'
        
        html += '</div>'
        return html 