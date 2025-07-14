document.addEventListener("DOMContentLoaded", () => {
  const toggle = document.getElementById("themeToggle");
  if (toggle) {
    if (localStorage.getItem("theme") === "dark") {
      document.body.classList.add("dark-mode");
    }

    toggle.addEventListener("click", () => {
      document.body.classList.toggle("dark-mode");
      if (document.body.classList.contains("dark-mode")) {
        localStorage.setItem("theme", "dark");
      } else {
        localStorage.setItem("theme", "light");
      }
    });
  }

  updateProgress(); 
});

function updateProgress() {
  const items = document.querySelectorAll("#taskList li");
  const completed = document.querySelectorAll("#taskList li.completed");
  const progressText = document.getElementById("progress");
  if (progressText) {
    progressText.innerText = `You’ve completed ${completed.length} of ${items.length} tasks`;
  }
}

function searchTasks() {
  const keyword = document.getElementById("searchInput").value;
  $.get("/search_tasks", { q: keyword }, function (data) {
    let taskList = $("#taskList");
    taskList.empty();

    if (data.length === 0) {
      taskList.append("<li>No tasks found.</li>");
    } else {
      data.forEach((task) => {
        const completeClass = task.completed ? "completed" : "";
        const categoryBadge = task.category
          ? `<span style="background:
              ${
                task.category === "Urgent"
                  ? "#ff4c4c"
                  : task.category === "Important"
                  ? "#ffac33"
                  : "#4caf50"
              };
              color:white; padding:4px 8px;
              border-radius:8px; margin-left:10px;
              font-size:12px;">${task.category}</span>`
          : "";

        const item = `
          <li class="${completeClass}">
            <span>${task.text} ${categoryBadge}</span>
            <div class="actions">
              <a href="/toggle_complete/${task.id}" title="Mark Complete">✅</a>
              <form action="/edit_task/${task.id}" method="POST" class="inline-form">
                <input type="text" name="new_text" placeholder="Edit..." required maxlength="255">
                <button type="submit" title="Edit Task">✏️</button>
              </form>
              <a href="/delete_task/${task.id}" title="Delete Task">❌</a>
            </div>
          </li>`;
        taskList.append(item);
      });
    }

    updateProgress();
  });
}
