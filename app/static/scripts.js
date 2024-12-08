document.addEventListener("DOMContentLoaded", function() {
    console.log("DOMContentLoaded event fired");
    var nearDeadlineTasks = JSON.parse(document.getElementById("near-deadline-tasks").textContent);
    console.log("Near deadline tasks:", nearDeadlineTasks);
    
    if (nearDeadlineTasks.length > 0) {
        nearDeadlineTasks.forEach(function(task) {
            if (shouldShowModal(task.id)) {
                console.log("Alerting about task:", task.title);
                showDeadlineModal(task.title, task.deadline, task.id);
            }
        });
    }
});

function showDeadlineModal(taskTitle, taskDeadline, taskId) {
    var modal = new bootstrap.Modal(document.getElementById('deadlineModal'));
    document.getElementById('taskTitle').textContent = taskTitle;
    document.getElementById('taskDeadline').textContent = new Date(taskDeadline).toLocaleString();
    document.getElementById('taskLink').href = `/tasks/${taskId}`;
    modal.show();
    // Обновляем время последнего показа для этой задачи
    localStorage.setItem('lastShownTime_' + taskId, new Date().getTime());
}

function shouldShowModal(taskId) {
    var lastShownTime = localStorage.getItem('lastShownTime_' + taskId);
    var currentTime = new Date().getTime();
    var oneHour = 60 * 60 * 1000; // 1 час в миллисекундах

    if (!lastShownTime || (currentTime - lastShownTime) > oneHour) {
        return true;
    }
    return false;
}