const api = {
  employees: "/api/employees",
  departments: "/api/departments",
  payrollRecords: "/api/payroll-records",
  summary: "/api/summary",
};

let departmentCache = [];
let employeeCache = [];

const formatCurrency = (value) =>
  Number(value || 0).toLocaleString("en-PH", {
    style: "currency",
    currency: "PHP",
    minimumFractionDigits: 2,
  });

async function fetchJSON(url, options = {}) {
  const response = await fetch(url, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(error.error || "Something went wrong");
  }
  return response.json();
}

async function loadSummary() {
  try {
    const summary = await fetchJSON(api.summary);
    document.getElementById("metric-employees").textContent =
      summary.totalEmployees;
    document.getElementById("metric-departments").textContent =
      summary.totalDepartments;
    document.getElementById("metric-payroll").textContent = formatCurrency(
      summary.totalNetPay
    );
    document.getElementById("metric-periods").textContent = summary.periods;
  } catch (error) {
    console.error(error);
  }
}

function refreshDepartmentSelects() {
  const createSelect = document.getElementById("department-select");
  const editSelect = document.querySelector(
    "#employee-edit-form select[name='department_id']"
  );

  if (!departmentCache.length) {
    const emptyOption = `<option value="">Create a department first</option>`;
    createSelect.innerHTML = emptyOption;
    if (editSelect) editSelect.innerHTML = emptyOption;
    return;
  }

  const optionsMarkup = departmentCache
    .map(
      (dept) =>
        `<option value="${dept.id}">${dept.name} (${dept.employee_count})</option>`
    )
    .join("");

  createSelect.innerHTML = optionsMarkup;
  if (editSelect) {
    editSelect.innerHTML = departmentCache
      .map((dept) => `<option value="${dept.id}">${dept.name}</option>`)
      .join("");
  }
}

async function loadDepartments() {
  const { data } = await fetchJSON(api.departments);
  departmentCache = data;

  const list = document.getElementById("department-list");

  if (!data.length) {
    list.innerHTML = '<li class="empty">No departments yet.</li>';
  } else {
    list.innerHTML = data
      .map(
        (dept) =>
          `<li>${dept.name} — ${dept.employee_count} ${
            dept.employee_count === 1 ? "employee" : "employees"
          }</li>`
      )
      .join("");
  }

  refreshDepartmentSelects();
}

async function loadEmployees(search = "") {
  const url = search ? `${api.employees}?q=${encodeURIComponent(search)}` : api.employees;
  const tableBody = document.getElementById("employee-body");
  const employeeSelect = document.getElementById("payroll-employee");
  const { data } = await fetchJSON(url);
  employeeCache = data;

  if (!data.length) {
    tableBody.innerHTML =
      '<tr><td colspan="6">No employees yet. Add one using the form above.</td></tr>';
    employeeSelect.innerHTML = '<option value="">Add employees first</option>';
    return;
  }

  tableBody.innerHTML = data
    .map(
      (emp) => `
      <tr>
        <td>${emp.full_name}</td>
        <td>${emp.email}</td>
        <td>${emp.department || "—"}</td>
        <td>${formatCurrency(emp.base_rate)}</td>
        <td>${emp.employment_type.replace("_", " ")}</td>
        <td>
          <div class="action-buttons">
            <button class="action-btn" data-action="edit-employee" data-id="${emp.id}">Edit</button>
            <button class="action-btn delete" data-action="delete-employee" data-id="${emp.id}">Delete</button>
          </div>
        </td>
      </tr>`
    )
    .join("");

  employeeSelect.innerHTML = data
    .map((emp) => `<option value="${emp.id}">${emp.full_name}</option>`)
    .join("");
}

async function loadPayrollRecords() {
  const tableBody = document.getElementById("payroll-body");
  const { data } = await fetchJSON(api.payrollRecords);
  tableBody.innerHTML = data
    .map(
      (record) => `
      <tr>
        <td>${record.employee?.full_name ?? ""}</td>
        <td>${record.period?.label ?? ""}</td>
        <td>${record.hours_worked}</td>
        <td>${formatCurrency(record.gross_pay)}</td>
        <td>${formatCurrency(record.net_pay)}</td>
        <td>${record.notes || "—"}</td>
      </tr>`
    )
    .join("");
}

function attachFormHandlers() {
  const employeeForm = document.getElementById("employee-form");
  const payrollForm = document.getElementById("payroll-form");
  const employeeFeedback = document.getElementById("employee-feedback");
  const payrollFeedback = document.getElementById("payroll-feedback");
  const departmentForm = document.getElementById("department-form");
  const departmentFeedback = document.getElementById("department-feedback");

  employeeForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    const formData = new FormData(employeeForm);
    const payload = Object.fromEntries(formData.entries());
    payload.base_rate = parseFloat(payload.base_rate);

    try {
      await fetchJSON(api.employees, {
        method: "POST",
        body: JSON.stringify(payload),
      });
      employeeFeedback.style.color = "#475467";
      employeeFeedback.textContent = "Employee saved!";
      employeeForm.reset();
      await loadSummary();
      await loadEmployees();
    } catch (error) {
      employeeFeedback.textContent = error.message;
      employeeFeedback.style.color = "#b42318";
    }
  });

  payrollForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    const formData = new FormData(payrollForm);
    const payload = Object.fromEntries(formData.entries());

    ["hours_worked", "hourly_rate", "tax_rate", "other_deductions"].forEach(
      (key) => {
        if (payload[key]) payload[key] = Number(payload[key]);
      }
    );

    try {
      await fetchJSON(api.payrollRecords, {
        method: "POST",
        body: JSON.stringify(payload),
      });
      payrollFeedback.style.color = "#475467";
      payrollFeedback.textContent = "Payroll recorded!";
      payrollForm.reset();
      await loadSummary();
      await loadPayrollRecords();
    } catch (error) {
      payrollFeedback.textContent = error.message;
      payrollFeedback.style.color = "#b42318";
    }
  });

  departmentForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    const formData = new FormData(departmentForm);
    const payload = Object.fromEntries(formData.entries());
    try {
      await fetchJSON(api.departments, {
        method: "POST",
        body: JSON.stringify(payload),
      });
      departmentFeedback.style.color = "#475467";
      departmentFeedback.textContent = "Department created!";
      departmentForm.reset();
      await loadDepartments();
    } catch (error) {
      departmentFeedback.textContent = error.message;
      departmentFeedback.style.color = "#b42318";
    }
  });
}

function attachSearchHandler() {
  const input = document.getElementById("employee-search");
  input.addEventListener("input", (event) => {
    loadEmployees(event.target.value);
  });
}

function openEmployeeModal(employeeId) {
  const employee = employeeCache.find((emp) => emp.id === employeeId);
  if (!employee) return;

  const modal = document.getElementById("employee-modal");
  const form = document.getElementById("employee-edit-form");
  const feedback = document.getElementById("employee-edit-feedback");
  feedback.textContent = "";

  refreshDepartmentSelects();

  form.elements.id.value = employee.id;
  form.elements.first_name.value = employee.first_name;
  form.elements.last_name.value = employee.last_name;
  form.elements.email.value = employee.email;
  form.elements.base_rate.value = employee.base_rate;
  form.elements.department_id.value = employee.department_id;
  form.elements.employment_type.value = employee.employment_type;
  form.elements.hire_date.value = employee.hire_date;

  modal.classList.add("open");
  form.elements.first_name.focus();
}

function closeEmployeeModal() {
  document.getElementById("employee-modal").classList.remove("open");
}

function attachEmployeeActions() {
  const tableBody = document.getElementById("employee-body");
  const modal = document.getElementById("employee-modal");
  const editForm = document.getElementById("employee-edit-form");
  const feedback = document.getElementById("employee-edit-feedback");

  tableBody.addEventListener("click", async (event) => {
    const button = event.target.closest("button[data-action]");
    if (!button) return;
    const employeeId = Number(button.dataset.id);
    if (button.dataset.action === "edit-employee") {
      openEmployeeModal(employeeId);
      return;
    }

    if (button.dataset.action === "delete-employee") {
      const confirmDelete = window.confirm(
        "Delete this employee record? This cannot be undone."
      );
      if (!confirmDelete) return;
      try {
        await fetchJSON(`${api.employees}/${employeeId}`, { method: "DELETE" });
        await loadEmployees();
        await loadSummary();
      } catch (error) {
        alert(error.message);
      }
    }
  });

  modal.addEventListener("click", (event) => {
    if (event.target.hasAttribute("data-modal-dismiss")) {
      closeEmployeeModal();
    }
  });

  editForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    const formData = new FormData(editForm);
    const payload = Object.fromEntries(formData.entries());
    const employeeId = payload.id;
    delete payload.id;
    payload.base_rate = Number(payload.base_rate);
    try {
      await fetchJSON(`${api.employees}/${employeeId}`, {
        method: "PUT",
        body: JSON.stringify(payload),
      });
      feedback.style.color = "#475467";
      feedback.textContent = "Employee updated!";
      await loadEmployees();
      await loadSummary();
      closeEmployeeModal();
    } catch (error) {
      feedback.style.color = "#b42318";
      feedback.textContent = error.message;
    }
  });
}

function initEstimator() {
  const hourlyInput = document.getElementById("est-hourly");
  if (!hourlyInput) return;

  const hoursInput = document.getElementById("est-hours");
  const taxInput = document.getElementById("est-tax");
  const deductionsInput = document.getElementById("est-deductions");
  const grossEl = document.getElementById("est-gross");
  const taxAmountEl = document.getElementById("est-tax-amount");
  const netEl = document.getElementById("est-net");
  const hoursValue = document.getElementById("est-hours-value");
  const taxValue = document.getElementById("est-tax-value");

  const recalc = () => {
    const hourly = Number(hourlyInput.value) || 0;
    const hours = Number(hoursInput.value) || 0;
    const taxPercent = Number(taxInput.value) || 0;
    const deductions = Number(deductionsInput.value) || 0;
    const gross = hourly * hours;
    const taxAmount = gross * (taxPercent / 100);
    const net = Math.max(gross - taxAmount - deductions, 0);

    hoursValue.textContent = `${hours} hrs`;
    taxValue.textContent = `${taxPercent}%`;
    grossEl.textContent = formatCurrency(gross);
    taxAmountEl.textContent = formatCurrency(taxAmount);
    netEl.textContent = formatCurrency(net);
  };

  [hourlyInput, hoursInput, taxInput, deductionsInput].forEach((input) =>
    input.addEventListener("input", recalc)
  );

  recalc();
}

document.addEventListener("DOMContentLoaded", async () => {
  await Promise.all([loadSummary(), loadDepartments()]);
  await loadEmployees();
  await loadPayrollRecords();
  attachFormHandlers();
  attachSearchHandler();
  attachEmployeeActions();
  initEstimator();
});

