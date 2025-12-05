const api = {
  employees: "/api/employees",
  departments: "/api/departments",
  payrollRecords: "/api/payroll-records",
  summary: "/api/summary",
};

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

async function loadDepartments() {
  const { data } = await fetchJSON(api.departments);
  const select = document.getElementById("department-select");
  const list = document.getElementById("department-list");

  if (!data.length) {
    select.innerHTML = `<option value="">Create a department first</option>`;
    list.innerHTML = '<li class="empty">No departments yet.</li>';
    return;
  }

  select.innerHTML = data
    .map(
      (dept) =>
        `<option value="${dept.id}">${dept.name} (${dept.employee_count})</option>`
    )
    .join("");

  list.innerHTML = data
    .map(
      (dept) =>
        `<li>${dept.name} — ${dept.employee_count} ${
          dept.employee_count === 1 ? "employee" : "employees"
        }</li>`
    )
    .join("");
}

async function loadEmployees(search = "") {
  const url = search ? `${api.employees}?q=${encodeURIComponent(search)}` : api.employees;
  const tableBody = document.getElementById("employee-body");
  const employeeSelect = document.getElementById("payroll-employee");
  const { data } = await fetchJSON(url);

  if (!data.length) {
    tableBody.innerHTML =
      '<tr><td colspan="5">No employees yet. Add one using the form above.</td></tr>';
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

document.addEventListener("DOMContentLoaded", async () => {
  await Promise.all([loadSummary(), loadDepartments()]);
  await loadEmployees();
  await loadPayrollRecords();
  attachFormHandlers();
  attachSearchHandler();
});

