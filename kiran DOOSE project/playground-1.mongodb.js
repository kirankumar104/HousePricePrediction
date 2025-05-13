/* global use, db */
// MongoDB Playground for Software Personnel Management System

// Use the database
use('personnel_management')

// Create "employees" collection
db.createCollection("employees")

// Create "modules" collection
db.createCollection("modules")

// Create "admin" collection
db.createCollection("admin")

// Insert sample employee
db.employees.insertOne({
  username: "john_doe",
  password: "1234",  // Plain text for testing
  name: "John Doe",
  designation: "Developer",
  login_time: null,
  logout_time: null
})

// Insert module record for the employee
db.modules.insertOne({
  employee_username: "john_doe",
  assigned_modules: [],
  completed_modules: []
})

// Insert admin user
db.admin.insertOne({
  username: "admin",
  password: "1234"  // Plain text for testing
})
