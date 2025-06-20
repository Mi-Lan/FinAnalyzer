#!/usr/bin/env node

/**
 * Update README.md progress table from tasks.json
 * Usage: node scripts/update-readme-progress.js
 */

const fs = require('fs');
const path = require('path');

// File paths
const TASKS_FILE = '.taskmaster/tasks/tasks.json';
const README_FILE = 'README.md';

// Status icons mapping
const STATUS_ICONS = {
  'done': '✅',
  'in-progress': '🔄', 
  'pending': '⏳',
  'blocked': '🔒',
  'deferred': '⏸️',
  'cancelled': '❌',
  'review': '👀'
};

function loadTasks() {
  try {
    const tasksData = JSON.parse(fs.readFileSync(TASKS_FILE, 'utf8'));
    // Handle both tagged and non-tagged task structures
    return tasksData.master?.tasks || tasksData.tags?.master?.tasks || tasksData.tasks || [];
  } catch (error) {
    console.error('Error reading tasks file:', error.message);
    process.exit(1);
  }
}

function generateProgressTable(tasks) {
  const completedTasks = tasks.filter(task => task.status === 'done').length;
  const totalTasks = tasks.length;
  const percentage = Math.round((completedTasks / totalTasks) * 100);

  let table = `## Development Progress\n\n`;
  table += `**Overall Progress: ${completedTasks}/${totalTasks} tasks completed (${percentage}%)**\n\n`;
  table += `| ID | Task | Status | Priority | Dependencies |\n`;
  table += `|:---|:-----|:-------|:---------|:-------------|\n`;

  tasks.forEach(task => {
    const icon = STATUS_ICONS[task.status] || '❓';
    const deps = task.dependencies?.length ? task.dependencies.join(', ') : 'none';
    const title = task.title.length > 50 ? task.title.substring(0, 47) + '...' : task.title;
    
    table += `| ${task.id} | ${title} | ${icon} ${task.status} | ${task.priority} | ${deps} |\n`;
  });

  return table;
}

function updateReadme(newProgressSection) {
  try {
    let readme = fs.readFileSync(README_FILE, 'utf8');
    
    // Find the progress section and replace it
    const progressStart = readme.indexOf('## Development Progress');
    const nextSectionStart = readme.indexOf('\n## ', progressStart + 1);
    
    if (progressStart === -1) {
      console.error('Progress section not found in README.md');
      process.exit(1);
    }
    
    const before = readme.substring(0, progressStart);
    const after = nextSectionStart === -1 ? '' : readme.substring(nextSectionStart);
    
    const updatedReadme = before + newProgressSection + '\n' + after;
    
    fs.writeFileSync(README_FILE, updatedReadme, 'utf8');
    console.log('✅ README.md progress table updated successfully');
    
  } catch (error) {
    console.error('Error updating README:', error.message);
    process.exit(1);
  }
}

function main() {
  console.log('🔄 Updating README progress table...');
  
  const tasks = loadTasks();
  console.log(`📋 Found ${tasks.length} tasks`);
  
  const progressSection = generateProgressTable(tasks);
  updateReadme(progressSection);
  
  console.log('✨ Update complete!');
}

// Run the script
if (require.main === module) {
  main();
} 