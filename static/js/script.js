document.addEventListener('DOMContentLoaded', function() {
    // DOM Elements
    const grammarInput = document.getElementById('grammar-input');
    const parseBtn = document.getElementById('parse-btn');
    const loadExampleBtn = document.getElementById('load-example');
    const resultsSection = document.getElementById('results-section');
    const errorMessage = document.getElementById('error-message');
    const tabButtons = document.querySelectorAll('.tab-btn');
    const tabContents = document.querySelectorAll('.tab-content');
    
    // Parse Button Click Handler
    parseBtn.addEventListener('click', function() {
        const grammar = grammarInput.value.trim();
        
        if (!grammar) {
            showError('Please enter a grammar.');
            return;
        }
        
        // Show loading state
        parseBtn.textContent = 'Generating...';
        parseBtn.disabled = true;
        hideError();
        
        // Send grammar to server
        fetch('/parse', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: 'grammar=' + encodeURIComponent(grammar)
        })
        .then(response => response.json())
        .then(data => {
            // Reset button state
            parseBtn.textContent = 'Generate SLR Parsing Table';
            parseBtn.disabled = false;
            
            if (data.success) {
                // Show results
                document.getElementById('parsing-table-content').innerHTML = data.parsing_table;
                document.getElementById('canonical-collection-content').innerHTML = data.canonical_collection;
                document.getElementById('first-follow-content').innerHTML = data.first_follow_sets;
                document.getElementById('grammar-content').textContent = data.grammar;
                
                resultsSection.classList.remove('hidden');
                scrollToResults();
            } else {
                showError(data.error || 'An error occurred while parsing the grammar.');
            }
        })
        .catch(error => {
            parseBtn.textContent = 'Generate SLR Parsing Table';
            parseBtn.disabled = false;
            showError('Network error: ' + error.message);
        });
    });
    
    // Load Example Button Click Handler
    loadExampleBtn.addEventListener('click', function() {
        fetch('/example')
            .then(response => response.json())
            .then(data => {
                grammarInput.value = data.grammar;
            })
            .catch(error => {
                showError('Error loading example: ' + error.message);
            });
    });
    
    // Tab Navigation
    tabButtons.forEach(button => {
        button.addEventListener('click', function() {
            // Remove active class from all buttons and contents
            tabButtons.forEach(btn => btn.classList.remove('active'));
            tabContents.forEach(content => content.classList.remove('active'));
            
            // Add active class to clicked button and corresponding content
            button.classList.add('active');
            const tabId = button.getAttribute('data-tab');
            document.getElementById(tabId).classList.add('active');
        });
    });
    
    // Helper Functions
    function showError(message) {
        errorMessage.textContent = message;
        errorMessage.classList.remove('hidden');
        resultsSection.classList.add('hidden');
    }
    
    function hideError() {
        errorMessage.classList.add('hidden');
    }
    
    function scrollToResults() {
        resultsSection.scrollIntoView({ behavior: 'smooth' });
    }
}); 