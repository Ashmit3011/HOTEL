function onScanSuccess(decodedText, decodedResult) {
    console.log(`QR Code matched = ${decodedText}`);
    document.getElementById('scan-result').innerText = `✅ Scanned: ${decodedText}`;
    
    // Redirect user to scanned URL (can be a table-specific link)
    if (decodedText.startsWith("http://") || decodedText.startsWith("https://")) {
        window.location.href = decodedText;
    } else {
        alert("Invalid QR Code content.");
    }
}

function onScanFailure(error) {
    // Optional: console.log(`QR Code scan error: ${error}`);
}

window.addEventListener('DOMContentLoaded', () => {
    const qrScanner = new Html5QrcodeScanner(
        "reader", {
            fps: 10,
            qrbox: { width: 250, height: 250 }
        });

    qrScanner.render(onScanSuccess, onScanFailure);
});
