
function openPhotoModal() {
    document.getElementById('photoModal').style.display = 'block';
    document.body.style.overflow = 'hidden';
}

function closePhotoModal() {
    document.getElementById('photoModal').style.display = 'none';
    document.body.style.overflow = 'auto';
}

// Close modal when clicking outside the content
document.getElementById('photoModal').addEventListener('click', function (e) {
    if (e.target === this) {
        closePhotoModal();
    }
});

// Close modal with escape key
document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') {
        closePhotoModal();
    }
});

document.addEventListener('DOMContentLoaded', function () {
    const starRatings = document.querySelectorAll('.star-rating');

    starRatings.forEach(ratingGroup => {
        const stars = ratingGroup.querySelectorAll('.fa-star');
        const inputName = ratingGroup.dataset.ratingInput;
        const hiddenInput = ratingGroup.querySelector(`input[name="${inputName}"]`);

        stars.forEach(star => {
            star.addEventListener('mouseover', function () {
                const value = this.dataset.value;
                highlightStars(stars, value);
            });

            star.addEventListener('mouseout', function () {
                if (!hiddenInput.value) {
                    clearStars(stars);
                } else {
                    highlightStars(stars, hiddenInput.value);
                }
            });

            star.addEventListener('click', function () {
                const value = this.dataset.value;
                hiddenInput.value = value;
                highlightStars(stars, value);
            });
        });
    });

    function highlightStars(stars, value) {
        stars.forEach(star => {
            const starValue = star.dataset.value;
            if (starValue <= value) {
                star.classList.add('active');
            } else {
                star.classList.remove('active');
            }
        });
    }

    function clearStars(stars) {
        stars.forEach(star => star.classList.remove('active'));
    }
});
