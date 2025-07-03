document.addEventListener('DOMContentLoaded', () => {
    const resultsDiv = document.getElementById('results');

    // Check if the resultsDiv exists and contains content indicative of results being present
    // (e.g., by checking for a specific child element or class that only appears with results)
    // For this example, we'll assume its presence means we should animate it.
    // A more robust check might be needed depending on how templates render empty states.
    if (resultsDiv && resultsDiv.innerHTML.trim() !== '') {
        // Initially hide the results for animation
        resultsDiv.classList.add('fade-in-up-start');

        // Trigger the animation
        // Using a small timeout to ensure the initial state is applied before animg
        setTimeout(() => {
            resultsDiv.classList.add('fade-in-up-active');
        }, 50); // 50ms delay
    }

    // Example: Smooth scroll to results if they are present and below the fold
    // This is just an idea, can be refined or removed if not desired.
    if (resultsDiv && resultsDiv.innerHTML.trim() !== '' && window.scrollY > resultsDiv.offsetTop - window.innerHeight + 100) {
        // resultsDiv.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }

    // You can add more JavaScript interactions here, for example:
    // - Form validation feedback
    // - Dynamic updates without full page reload (more advanced, would require AJAX)
});
