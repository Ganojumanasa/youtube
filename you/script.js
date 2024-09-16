document.getElementById('downloadForm').addEventListener('submit', async function(event) {
    event.preventDefault();

    const url = document.getElementById('playlistUrl').value;
    const messageDiv = document.getElementById('message');

    try {
        const response = await fetch('http://localhost:8001/download', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ playlist_url: url })
        });

        if (!response.ok) {
            throw new Error('Failed to start download');
        }

        const result = await response.json();
        messageDiv.textContent = result.message;
        messageDiv.style.color = 'green';

    } catch (error) {
        messageDiv.textContent = error.message;
        messageDiv.style.color = 'red';
    }
});
