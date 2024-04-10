document.addEventListener('DOMContentLoaded', function() {
    var form = document.getElementById('waitlist-form');
    
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        var formData = new FormData(form);
        
        fetch('/ml-join-waitlist', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if(data.status === 'success') {
                document.getElementById('container').innerHTML = data.html;
            } else {
                document.getElementById('container').innerHTML = '<p>Failed to subscribe. Please try again.</p>';
            }
        })
        .catch(error => {
            document.getElementById('container').innerHTML = '<p>Error occurred. Please try again later.</p>';
        });
    });
});
