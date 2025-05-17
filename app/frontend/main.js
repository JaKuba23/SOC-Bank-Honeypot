async function fetchMe() {
    const res = await fetch('http://localhost:5000/api/me', {credentials: 'include'});
    if (res.status !== 200) {
        window.location.href = "login.html";
        return;
    }
    const data = await res.json();
    document.getElementById('userInfo').innerHTML = `
        <b>Logged in as:</b> ${data.fullname}<br>
        <b>Account:</b> ${data.account}<br>
        <b>Balance:</b> ${data.balance.toFixed(2)} EUR
    `;
}

async function fetchRecipients() {
    const res = await fetch('http://localhost:5000/api/users', {credentials: 'include'});
    const users = await res.json();
    const select = document.getElementById('recipient');
    select.innerHTML = '';
    users.forEach(u => {
        const opt = document.createElement('option');
        opt.value = u.account;
        opt.textContent = `${u.fullname} (${u.account})`;
        select.appendChild(opt);
    });
}

document.getElementById('logoutBtn').onclick = async function() {
    await fetch('http://localhost:5000/api/logout', {method: 'POST', credentials: 'include'});
    window.location.href = "login.html";
};

document.getElementById('socDashboardBtn').onclick = function() {
    window.open('soc_dashboard.html', '_blank');
};

document.getElementById('transferForm').onsubmit = async function(e) {
    e.preventDefault();
    document.getElementById('resultSection').style.display = 'none';
    document.getElementById('errorSection').style.display = 'none';
    const recipient_account = document.getElementById('recipient').value;
    const amount = document.getElementById('amount').value;
    const res = await fetch('http://localhost:5000/api/transfer', {
        method: 'POST',
        credentials: 'include',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({recipient_account, amount})
    });
    const data = await res.json();
    if (res.status === 200) {
        document.getElementById('resultSection').textContent = `Transfer successful! New balance: ${data.new_balance.toFixed(2)} EUR`;
        document.getElementById('resultSection').style.display = 'block';
        fetchMe();
    } else {
        document.getElementById('errorSection').textContent = data.error;
        document.getElementById('errorSection').style.display = 'block';
    }
};

window.onload = function() {
    fetchMe();
    fetchRecipients();
};