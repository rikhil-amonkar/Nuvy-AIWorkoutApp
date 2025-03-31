document.addEventListener("DOMContentLoaded", () => {
    const searchInput = document.getElementById('search');
    const dropdown = document.getElementById('autocomplete-results');

    if (searchInput) {
        searchInput.addEventListener('input', function() {
            let query = this.value.trim();
            
            if (query.length > 1) {
                fetch(`/logger/search?q=${query}`)
                    .then(response => response.json())
                    .then(data => {
                        dropdown.innerHTML = '';

                        if (data.length === 0) {
                            dropdown.style.display = 'none';
                            return;
                        }

                        data.forEach(item => {
                            let div = document.createElement('div');
                            div.textContent = item;
                            div.addEventListener('click', function() {
                                searchInput.value = item;
                                dropdown.style.display = 'none';
                            });
                            dropdown.appendChild(div);
                        });

                        dropdown.style.display = 'block';
                    });
            } else {
                dropdown.style.display = 'none';
            }
        });

        document.addEventListener('click', (e) => {
            if (e.target !== searchInput) {
                dropdown.style.display = 'none';
            }
        });
    }
});
