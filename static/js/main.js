// Main JavaScript for BCA Department Management System

document.addEventListener("DOMContentLoaded", function() {
    // 1. Animated Counters on Homepage
    const counters = document.querySelectorAll(".counter-val");
    if (counters.length > 0) {
        const runCounters = () => {
            counters.forEach(counter => {
                const target = parseInt(counter.getAttribute("data-target"), 10);
                const count = parseInt(counter.innerText, 10) || 0;
                const speed = 200; // Alter duration
                const increment = target / speed;
                
                if (count < target) {
                    counter.innerText = Math.ceil(count + increment);
                    setTimeout(runCounters, 1);
                } else {
                    counter.innerText = target;
                }
            });
        };
        
        // Simple Intersection Observer to start counter when visible
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    runCounters();
                    observer.unobserve(entry.target);
                }
            });
        }, { threshold: 0.5 });
        
        const targetSection = document.querySelector(".counter-section");
        if (targetSection) {
            observer.observe(targetSection);
        } else {
            // Run immediately if observer target is missing
            runCounters();
        }
    }

    // 2. Auto-dismiss flash messages after 5 seconds
    setTimeout(function() {
        const alerts = document.querySelectorAll('.alert-dismissible');
        alerts.forEach(function(alert) {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        });
    }, 5000);

    // 3. File Upload Checks (Front-end validation)
    const fileInputs = document.querySelectorAll('input[type="file"]');
    fileInputs.forEach(input => {
        input.addEventListener('change', function() {
            if (this.files && this.files[0]) {
                const file = this.files[0];
                const maxSize = 5 * 1024 * 1024; // 5MB limit
                
                // Show selected file name in drag-drop labels if exists
                const label = this.closest('.file-upload-wrapper')?.querySelector('.upload-label-text');
                if (label) {
                    label.innerText = file.name;
                }
                
                if (file.size > maxSize) {
                    alert(`File "${file.name}" exceeds the maximum allowed size of 5MB.`);
                    this.value = ''; // Reset file input
                    if (label) {
                        label.innerText = "Drag and drop or browse file";
                    }
                }
            }
        });
    });

    // 4. Mock Card Payment Inputs Formatting
    const cardNumberInput = document.getElementById('cardNumber');
    if (cardNumberInput) {
        cardNumberInput.addEventListener('input', function(e) {
            let value = e.target.value.replace(/\s+/g, '').replace(/[^0-9]/gi, '');
            let matches = value.match(/\d{4,16}/g);
            let match = matches && matches[0] || '';
            let parts = [];

            for (let i = 0, len = match.length; i < len; i += 4) {
                parts.push(match.substring(i, i + 4));
            }

            if (parts.length > 0) {
                e.target.value = parts.join(' ');
            } else {
                e.target.value = value;
            }
        });
    }

    const cardExpiryInput = document.getElementById('cardExpiry');
    if (cardExpiryInput) {
        cardExpiryInput.addEventListener('input', function(e) {
            let value = e.target.value.replace(/\s+/g, '').replace(/[^0-9]/gi, '');
            if (value.length >= 2) {
                let month = value.substring(0, 2);
                let year = value.substring(2, 4);
                if (parseInt(month, 10) > 12) month = "12";
                e.target.value = month + '/' + year;
            } else {
                e.target.value = value;
            }
        });
    }

    // 5. Mock Payment Submission Animation
    const paymentForm = document.getElementById('paymentForm');
    if (paymentForm) {
        paymentForm.addEventListener('submit', function(e) {
            const submitBtn = document.getElementById('paySubmitBtn');
            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.innerHTML = `<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Processing Secure Payment...`;
            }
        });
    }
});
