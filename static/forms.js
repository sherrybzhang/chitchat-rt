const validatedForms = document.querySelectorAll("[data-validate-form]");

function getFieldErrorElement(field) {
  const errorId = field.dataset.errorId;
  return errorId ? document.getElementById(errorId) : null;
}

function setFieldError(field, message) {
  const errorElement = getFieldErrorElement(field);
  if (!errorElement) {
    return;
  }

  errorElement.textContent = message;
  errorElement.hidden = !message;

  if (message) {
    field.setAttribute("aria-invalid", "true");
  } else {
    field.removeAttribute("aria-invalid");
  }
}

function validateField(field) {
  if (field.checkValidity()) {
    setFieldError(field, "");
    return true;
  }

  setFieldError(field, field.validationMessage || "Please fill out this field.");
  return false;
}

validatedForms.forEach((form) => {
  form.noValidate = true;

  const fields = Array.from(form.querySelectorAll("[data-error-id]"));
  if (!fields.length) {
    return;
  }

  fields.forEach((field) => {
    field.addEventListener("input", () => {
      if (field.checkValidity()) {
        setFieldError(field, "");
      }
    });
  });

  form.addEventListener(
    "submit",
    (event) => {
      let firstInvalidField = null;

      fields.forEach((field) => {
        const isValid = validateField(field);
        if (!isValid && !firstInvalidField) {
          firstInvalidField = field;
        }
      });

      if (!firstInvalidField) {
        return;
      }

      event.preventDefault();
      event.stopImmediatePropagation();
      firstInvalidField.focus();
    },
    true,
  );
});
