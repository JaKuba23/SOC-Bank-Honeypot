const senderNames = [
    "Anna Nowak", "Jan Kowalski", "Maria Wiśniewska", "Piotr Zieliński", "Katarzyna Wójcik"
];
const recipientNames = [
    "Tomasz Kamiński", "Agnieszka Lewandowska", "Michał Dąbrowski", "Ewa Szymańska", "Paweł Kaczmarek"
];

function getRandom(arr) {
    return arr[Math.floor(Math.random() * arr.length)];
}

const sender = getRandom(senderNames);
let recipient;
do {
    recipient = getRandom(recipientNames);
} while (recipient === sender);

document.getElementById('senderName').textContent = sender;
document.getElementById('recipientName').textContent = recipient;

const form = document.getElementById('transferForm');
const amountInput = document.getElementById('amount');
const resultSection = document.getElementById('resultSection');
const conversionResultSpan = document.getElementById('conversionResult');
const errorSection = document.getElementById('errorSection');
const errorMessageP = document.getElementById('errorMessage');

form.addEventListener('submit', async (event) => {
    event.preventDefault();

    resultSection.style.display = 'none';
    errorSection.style.display = 'none';
    errorMessageP.textContent = '';
    conversionResultSpan.textContent = '';

    const amountStr = amountInput.value.trim();

    const amount = parseFloat(amountStr);
    if (isNaN(amount) || amount <= 0) {
        errorMessageP.textContent = "Please enter a valid positive amount.";
        errorSection.style.display = 'block';
        return;
    }

    try {
        const response = await fetch('http://127.0.0.1:5000/api/transfer', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ sender, recipient, amount })
        });
        const responseData = await response.json();

        if (!response.ok) {
            errorMessageP.textContent = responseData.error || `Server error: ${response.status}`;
            errorSection.style.display = 'block';
        } else {
            conversionResultSpan.textContent = responseData.pln.toFixed(2);
            resultSection.style.display = 'block';
        }
    } catch (error) {
        errorMessageP.textContent = "Cannot connect to server. Is the backend running?";
        errorSection.style.display = 'block';
    }
});