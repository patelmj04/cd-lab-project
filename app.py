from flask import Flask, render_template, request, jsonify
import os
from slr_parser import SLRParser

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/parse', methods=['POST'])
def parse():
    grammar_text = request.form.get('grammar', '')
    
    try:
        parser = SLRParser(grammar_text)
        
        result = {
            'success': True,
            'parsing_table': parser.get_parsing_table_html(),
            'canonical_collection': parser.get_canonical_collection_html(),
            'first_follow_sets': parser.get_first_follow_sets_html(),
            'grammar': str(parser.grammar)
        }
    except Exception as e:
        result = {
            'success': False,
            'error': str(e)
        }
    
    return jsonify(result)

@app.route('/example')
def example():
    example_grammar = """E -> E + T | T
T -> T * F | F
F -> ( E ) | id"""
    
    return jsonify({'grammar': example_grammar})

if __name__ == '__main__':
    app.run(debug=True) 