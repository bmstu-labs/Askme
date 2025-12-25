document.addEventListener('DOMContentLoaded', function() {
    function getCSRFToken() {
        const cookie = document.cookie.split('; ').find(row => row.startsWith('csrftoken='));
        return cookie ? cookie.split('=')[1] : '';
    }

    document.querySelectorAll('.vote-btn[data-question-id]').forEach(btn => {
        btn.addEventListener('click', function() {
            const questionId = this.dataset.questionId;
            const value = this.dataset.value;
            const container = this.closest('.text-center');
            
            if (!container) {
                console.error('Cannot find container element');
                return;
            }
            
            const countElement = container.querySelector('.vote-count');
            
            if (!countElement) {
                console.error('Cannot find vote-count element');
                return;
            }
            
            fetch(`/question/${questionId}/vote/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCSRFToken(),
                },
                body: JSON.stringify({ value: parseInt(value) })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    countElement.textContent = data.rating;
                    container.querySelectorAll('.vote-btn').forEach(b => b.disabled = true);
                    alert('Your vote has been recorded!');
                }
                else {
                    alert(data.error || 'Error: Could not record vote');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Network error. Please try again.');
            });
        });
    });

    document.querySelectorAll('.mark-correct-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const answerId = this.dataset.answerId;
            const questionId = this.dataset.questionId;
            
            if (!questionId) {
                console.error('Question ID is missing');
                return;
            }
            
            fetch(`/question/${questionId}/mark_correct/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCSRFToken(),
                },
                body: JSON.stringify({ answer_id: answerId })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    if (data.is_correct) {
                        this.textContent = 'Correct';
                        this.classList.add('btn-success');
                        this.classList.remove('btn-outline-success');
                        
                        const answerCard = document.querySelector(`[data-answer-id="${answerId}"]`);
                        if (answerCard) {
                            answerCard.classList.add('border-success');
                            answerCard.classList.add('border-2');
                        }
                        
                        document.querySelectorAll('.answer-card').forEach(card => {
                            if (card.dataset.answerId !== answerId) {
                                card.classList.remove('border-success', 'border-2');
                                const otherBtn = card.querySelector('.mark-correct-btn');
                                if (otherBtn) {
                                    otherBtn.textContent = 'Mark correct';
                                    otherBtn.classList.remove('btn-success');
                                    otherBtn.classList.add('btn-outline-success');
                                }
                            }
                        });
                    }
                    else {
                        this.textContent = 'Mark correct';
                        this.classList.remove('btn-success');
                        this.classList.add('btn-outline-success');
                        const answerCard = document.querySelector(`[data-answer-id="${answerId}"]`);
                        if (answerCard) {
                            answerCard.classList.remove('border-success', 'border-2');
                        }
                    }
                    
                    alert('Answer status updated!');
                }
                else {
                    alert(data.error || 'Error updating answer');
                }
            })
            .catch(() => alert('Network error'));
        });
    });
});