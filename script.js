document.addEventListener('DOMContentLoaded', () => {
    const datePicker = document.getElementById('date-picker');
    datePicker.value = new Date().toISOString().split('T')[0];
    loadEntries(datePicker.value);

    datePicker.addEventListener('change', () => {
        loadEntries(datePicker.value);
    });

    document.getElementById('workout-form').addEventListener('submit', (e) => {
        e.preventDefault();
        const workoutInput = document.getElementById('workout-input');
        addEntry('workout', datePicker.value, workoutInput.value);
        workoutInput.value = '';
    });

    document.getElementById('meal-form').addEventListener('submit', (e) => {
        e.preventDefault();
        const mealInput = document.getElementById('meal-input');
        addEntry('meal', datePicker.value, mealInput.value);
        mealInput.value = '';
    });
});

function loadEntries(date) {
    document.getElementById('selected-date').textContent = date;
    fetch(`/get_entries?date=${date}`)
        .then(response => response.json())
        .then(data => {
            const entryList = document.getElementById('entry-list');
            entryList.innerHTML = '';
            data.workouts.forEach(workout => {
                const li = document.createElement('li');
                li.textContent = `Training: ${workout}`;
                entryList.appendChild(li);
            });
            data.meals.forEach(meal => {
                const li = document.createElement('li');
                li.textContent = `Mahlzeit: ${meal}`;
                entryList.appendChild(li);
            });
        });
}

function addEntry(type, date, entry) {
    const url = type === 'workout' ? '/add_workout' : '/add_meal';
    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ date, [type]: entry })
    }).then(() => loadEntries(date));
}