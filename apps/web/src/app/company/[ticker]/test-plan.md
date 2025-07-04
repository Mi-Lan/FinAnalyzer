# Integration Test Plan for Backend Connection

**Task:** [Task 9: Display Scores & Insights in UI](/.taskmaster/tasks/tasks.json)
**Subtask:** [Subtask 9.5: Integration Testing](/.taskmaster/tasks/tasks.json)

This document outlines the manual testing steps to verify the successful integration of the Next.js frontend with the FastAPI backend, replacing all mock data sources.

### Pre-requisites

1.  Ensure all services (`web`, `api-gateway`, `database`, etc.) are running.
    ```bash
    docker-compose up --build
    ```
2.  Have the application open in your browser, typically at `http://localhost:3000`.
3.  Open the browser's developer console to monitor network requests and logs.

---

### Test Case 1: Fetching All Companies

**Objective:** Verify that the main dashboard correctly fetches and displays the list of all companies from the backend.

**Steps:**

1.  Navigate to the homepage (`/`).
2.  Observe the "All Companies" table.
3.  **Expected Result:** The table should populate with a list of companies.
4.  In the developer console's Network tab, confirm that a `GET` request to `/api/companies` was successful (Status 200 OK).
5.  Check the response of the `/api/companies` call. It should be a JSON object containing a `companies` array.

---

### Test Case 2: Fetching Company Details

**Objective:** Verify that navigating to a company-specific page fetches and displays detailed data for that company.

**Steps:**

1.  From the dashboard, click on any company in the "All Companies" table (e.g., "AAPL").
2.  You should be navigated to the company detail page (e.g., `/company/AAPL`).
3.  **Expected Result:** The page should display the company's name, ticker, and other details, along with financial metrics and analysis sections.
4.  In the developer console's Network tab, confirm a successful `GET` request to `/api/companies/AAPL`.
5.  Inspect the response to ensure it contains detailed financial data.

---

### Test Case 3: Company Screening

**Objective:** Verify that the screening/filtering functionality on the dashboard works with the backend.

**Steps:**

1.  On the dashboard, use the filtering options (e.g., select a Sector, set a minimum score).
2.  **Expected Result:** The "All Companies" table should update to show only the companies that match the filter criteria.
3.  In the developer console's Network tab, observe a `GET` request to `/api/analysis/screen` with the filter criteria included as query parameters (e.g., `?sector=Technology`).
4.  Confirm the request is successful and the returned data reflects the applied filters.

---

### Test Case 4: Template-Based Analysis (Streaming)

**Objective:** Verify that the analysis feature on the company detail page streams results from the backend.

**Steps:**

1.  Navigate to a company detail page (e.g., `/company/AAPL`).
2.  Click the "Run Analysis" button.
3.  **Expected Result:** The UI should show a loading state, and then progressively display the analysis results as they are streamed from the backend. You should see different parts of the analysis (profitability, growth, etc.) appear one by one.
4.  In the developer console's Network tab, find the `POST` request to `/api/analysis/template/tech-default-v1`.
5.  Verify that the response is of type `text/event-stream` and that you can see the data chunks arriving in the Response or EventStream tab.

---

### Test Case 5: Error Handling

**Objective:** Verify that the UI gracefully handles backend errors.

**Steps:**

1.  To simulate an error, you can temporarily stop the `api-gateway` container:
    ```bash
    docker-compose stop api-gateway
    ```
2.  Refresh the company detail page.
3.  **Expected Result:** The page should display a user-friendly error message (e.g., "Failed to fetch company details") instead of crashing.
4.  Restart the container to continue testing:
    ```bash
    docker-compose start api-gateway
    ```

---

By completing these tests, we can confirm that the frontend is correctly integrated with the backend services, fulfilling the requirements of subtasks 9.1 and 9.2.
