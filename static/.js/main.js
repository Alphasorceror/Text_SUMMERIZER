document.addEventListener('DOMContentLoaded', function () {
    // DOM elements
    const form = document.getElementById('summarize-form');
    const textInput = document.getElementById('text-input');
    const ratioRange = document.getElementById('ratio-range');
    const ratioValue = document.getElementById('ratio-value');
    const clearBtn = document.getElementById('clear-btn');
    const summarizeBtn = document.getElementById('summarize-btn');
    const textCounter = document.getElementById('text-counter');
    const resultContainer = document.getElementById('result-container');
    const summaryText = document.getElementById('summary-text');
    const errorContainer = document.getElementById('error-container');
    const errorMessage = document.getElementById('error-message');
    const copyBtn = document.getElementById('copy-btn');

    // Loading modal
    const loadingModalElement = document.getElementById('loading-modal');
    const loadingModal = new bootstrap.Modal(loadingModalElement);

    // Update ratio value display
    ratioRange.addEventListener('input', function () {
        ratioValue.textContent = `${this.value}%`;
    });

    // Update character count
    textInput.addEventListener('input', function () {
        const count = this.value.length;
        textCounter.textContent = `${count} characters`;

        // Enable/disable the summarize button based on text length
        summarizeBtn.disabled = count < 10;
    });

    // Clear form
    clearBtn.addEventListener('click', function () {
        textInput.value = '';
        ratioRange.value = 30;
        ratioValue.textContent = '30%';
        textCounter.textContent = '0 characters';
        document.getElementById('language-select').value = 'auto';
        hideResult();
        hideError();
        summarizeBtn.disabled = true;
    });

    // Copy summary to clipboard
    copyBtn.addEventListener('click', function () {
        const textToCopy = summaryText.textContent;
        navigator.clipboard.writeText(textToCopy).then(function () {
            // Change button text temporarily
            const originalText = copyBtn.innerHTML;
            copyBtn.innerHTML = '<i class="fas fa-check me-1"></i>Copied!';
            setTimeout(function () {
                copyBtn.innerHTML = originalText;
            }, 2000);
        }).catch(function (err) {
            console.error('Failed to copy text: ', err);
        });
    });

    // Fix for modal not closing properly
    loadingModalElement.addEventListener('hidden.bs.modal', function () {
        // Remove the modal backdrop if it's still there
        const modalBackdrops = document.querySelectorAll('.modal-backdrop');
        modalBackdrops.forEach(backdrop => {
            backdrop.remove();
        });
        // Remove modal-open class from body
        document.body.classList.remove('modal-open');
        document.body.style.overflow = '';
        document.body.style.paddingRight = '';
    });

    // Submit form
    form.addEventListener('submit', function (event) {
        event.preventDefault(); // Prevent page reload

        const text = textInput.value.trim();
        const ratio = parseInt(ratioRange.value) / 100;
        const language = document.getElementById('language-select').value;

        if (text.length < 10) {
            showError('Please provide a longer text to summarize (minimum 10 characters)');
            return;
        }

        hideError();

        // Show loading modal
        loadingModal.show();

        // Call API to summarize text
        fetch('/summarize', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                text: text,
                ratio: ratio,
                language: language
            })
        })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Failed to fetch summary');
                }
                return response.json();
            })
            .then(data => {
                // Hide the loading modal
                hideLoadingModal();

                if (data.error) {
                    showError(data.error);
                    hideResult();
                } else {
                    hideError();
                    showResult(data.summary);
                }
            })
            .catch(error => {
                // Hide the loading modal
                hideLoadingModal();

                showError('An error occurred while processing your request. Please try again.');
                console.error('Error:', error);
            });
    });

    // Helper functions
    function showError(message) {
        errorMessage.textContent = message;
        errorContainer.classList.remove('d-none');
    }

    function hideError() {
        errorContainer.classList.add('d-none');
    }

    function showResult(summary) {
        summaryText.textContent = summary;
        resultContainer.classList.remove('d-none');

        // Smooth scroll to results
        resultContainer.scrollIntoView({
            behavior: 'smooth',
            block: 'start'
        });
    }

    function hideResult() {
        resultContainer.classList.add('d-none');
    }

    function hideLoadingModal() {
        if (loadingModalElement.classList.contains('show')) {
            loadingModal.hide();
            // Force cleanup of modal
            document.body.classList.remove('modal-open');
            document.body.style.overflow = '';
            document.body.style.paddingRight = '';
            const backdrops = document.querySelectorAll('.modal-backdrop');
            backdrops.forEach(backdrop => backdrop.remove());
        }
    }

    // Initialize form state
    summarizeBtn.disabled = true;
});