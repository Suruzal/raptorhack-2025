document.getElementById('addUserForm').addEventListener('submit', async (e) => {
    e.preventDefault();

    const name = document.getElementById('name').value;
    const major = document.getElementById('major').value;

    const response = await fetch('http://127.0.0.1:5000/add_user', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name, major }),
    });

    if (response.ok) {
        alert('User added successfully!');
        document.getElementById('addUserForm').reset();
    } else {
        alert('Failed to add user.');
    }
});

async function fetchMatches(userId) {
    const response = await fetch('http://127.0.0.1:5000/match_users', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_id: userId }),
    });

    if (response.ok) {
        const matches = await response.json();
        const matchesList = document.getElementById('matchesList');
        matchesList.innerHTML = '';
        matches.forEach(match => {
            const li = document.createElement('li');
            li.textContent = `Match: ${match.partner_id}`;
            matchesList.appendChild(li);
        });
    } else {
        alert('Failed to fetch matches.');
    }
}