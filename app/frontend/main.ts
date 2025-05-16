// c:\Users\Jakub\Documents\GitHub\Currency-Phish-Honeypot\frontend\main.ts

const form = document.getElementById('conversionForm') as HTMLFormElement;
const amountInput = document.getElementById('amount') as HTMLInputElement;
const resultSection = document.getElementById('resultSection') as HTMLDivElement;
const conversionResultSpan = document.getElementById('conversionResult') as HTMLSpanElement;
const errorSection = document.getElementById('errorSection') as HTMLDivElement;
const errorMessageP = document.getElementById('errorMessage') as HTMLParagraphElement;
// Jeśli masz element do wyświetlania kursu, możesz go tu odkomentować i użyć,
// ale obecna wersja Twojego flask_app.py nie zwraca informacji o kursie.
// const rateInfoElement = document.getElementById('rateInfo') as HTMLElement;

form.addEventListener('submit', async (event) => {
    event.preventDefault(); // Zapobiegaj domyślnemu przeładowaniu strony

    const amountStr = amountInput.value;

    // Ukryj poprzednie wyniki/błędy
    resultSection.style.display = 'none';
    errorSection.style.display = 'none';
    errorMessageP.textContent = '';
    conversionResultSpan.textContent = '';
    // if (rateInfoElement) {
    //     rateInfoElement.textContent = '';
    //     rateInfoElement.style.display = 'none';
    // }


    if (!amountStr.trim()) {
        errorMessageP.textContent = "Proszę podać kwotę.";
        errorSection.style.display = 'block';
        return;
    }

    const amount = parseFloat(amountStr);

    if (isNaN(amount)) {
        errorMessageP.textContent = "Proszę podać poprawną liczbę jako kwotę.";
        errorSection.style.display = 'block';
        return;
    }
    
    if (amount < 0) {
        errorMessageP.textContent = "Kwota nie może być ujemna.";
        errorSection.style.display = 'block';
        return;
    }

    try {
        // Upewnij się, że Twój serwer Flask działa na http://127.0.0.1:5000
        const response = await fetch('http://127.0.0.1:5000/api/convert', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ amount: amount }),
        });

        const responseData = await response.json();

        if (!response.ok) {
            // Serwer zwrócił błąd (np. 400, 500)
            // Twoje flask_app.py zwraca {"error": "wiadomosc"}
            errorMessageP.textContent = responseData.error || `Błąd serwera: ${response.status}`;
            errorSection.style.display = 'block';
        } else {
            // Sukces, Twoje flask_app.py zwraca {"pln": kwota}
            conversionResultSpan.textContent = responseData.pln.toFixed(2);
            resultSection.style.display = 'block';
            
            // Jeśli chciałbyś wyświetlać kurs, musiałbyś zmodyfikować flask_app.py,
            // aby zwracał również 'rate_used', a następnie odkomentować poniższe:
            // if (responseData.rate_used && rateInfoElement) {
            //     rateInfoElement.textContent = `(kurs: 1 EUR = ${responseData.rate_used.toFixed(4)} PLN)`;
            //     rateInfoElement.style.display = 'block';
            // }
        }
    } catch (error) {
        console.error('Błąd Fetch:', error);
        errorMessageP.textContent = "Nie można połączyć się z serwerem. Sprawdź połączenie lub czy serwer jest uruchomiony.";
        errorSection.style.display = 'block';
    }
});