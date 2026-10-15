const form = document.querySelector("#task-form");

if (form) {
  const titleInput = document.querySelector("#title");
  const descriptionInput = document.querySelector("#description");
  const taskList = document.querySelector("#task-list");
  const emptyState = document.querySelector("#empty-state");
  const message = document.querySelector("#form-message");

  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    message.hidden = true;

    try {
      const response = await fetch("/tasks/add", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          title: titleInput.value,
          description: descriptionInput.value,
        }),
      });
      const result = await response.json();

      if (!response.ok) {
        throw new Error(result.error || "Could not add task.");
      }

      const item = document.createElement("li");
      item.className = "task-item";
      const title = document.createElement("strong");
      title.textContent = result.title;
      item.append(title);

      if (result.description) {
        const description = document.createElement("p");
        description.textContent = result.description;
        item.append(description);
      }

      taskList.prepend(item);
      emptyState.hidden = true;
      form.reset();
      titleInput.focus();
    } catch (error) {
      message.textContent = error.message;
      message.hidden = false;
    }
  });
}
