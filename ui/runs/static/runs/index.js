// === EVENT LISTENER ===

document.addEventListener('DOMContentLoaded', () => {
  // Delete Btns
  const delete_btns = document.querySelectorAll('.delete-btn');

  delete_btns.forEach(button => {
    const svg = button.querySelector('svg');

    button.addEventListener('mouseover', () => {
        button.classList.add('btn-red');
        button.classList.remove('btn-grey');
        if (svg) svg.setAttribute('fill', 'white');
    });

    button.addEventListener('mouseout', () => {
        button.classList.add('btn-grey');
        button.classList.remove('btn-red');
        if (svg) svg.setAttribute('fill', 'grey');
    });
  });

  // mark first run as selected
  let first_run = document.getElementById('run-1');
  first_run.style.backgroundColor = '#e8edf3';
  first_run.style.borderRadius = '10px';

  const clearButton = document.getElementById('clearFilters');
    if (clearButton) {
        clearButton.addEventListener('click', clearFilters);
    }

});


// === FUNCTIONS ===
function selectRun(runName, runId, numberOfRuns){
  for (let i = 1; i <= numberOfRuns; i++) {
      let run = document.getElementById('run-' + i);
      if (i == runId) {
        run.style.backgroundColor = 'rgb(232, 237, 243)';
        run.style.borderRadius = '10px';
      }
      else {
          run.style.backgroundColor = 'white';
      }
  }    

  document.getElementById('selectedRun').textContent = runName;
  document.getElementById('run_name_id').value = runName;
};

function deleteRun(runName){
  document.getElementById('delete_run_name_id').value = runName;
  document.getElementById('delete_run').submit();
};

function toggleFavouriteRun(runName){

  document.getElementById('favourites_run_name_id').value = runName;
  document.getElementById('change_favourite').submit();
};

function addTag(runName){
  document.getElementById('add_tag_run_name_id').value = runName;
  console.log(runName);
  document.getElementById('add_tag_name_id').value = document.getElementById('tag_name_id_' + runName).value;
  document.getElementById('add_tag').submit();
};

function deleteTag(runName, tagName){

  document.getElementById('delete_tag_run_name_id').value = runName;
  document.getElementById('delete_tag_name_id').value = tagName;
  document.getElementById('delete_tag').submit();
};

function toggleDetails(element) {
  document.querySelectorAll('.list-item.expanded').forEach(item => {
    if (item !== element) {
      item.classList.remove('expanded');
      item.querySelector('.details').style.display = 'none';
    }
  });

  const details = element.querySelector('.details');
  if (element.classList.contains('expanded')) {
    element.classList.remove('expanded');
    details.style.display = 'none';
    element.style.height = "40px";
  } else {
    element.classList.add('expanded');
    details.style.display = 'block';
    element.style.height = "250px";
  }
}

function clearFilters() {
    const form = document.getElementById('filtertest');


    // Clear text inputs
    form.querySelectorAll('input[type="text"]').forEach(input => input.value = '');

    // Clear search_steps
    const searchStepsMultiSelect = new MultiSelect(document.getElementById('search_steps'));
    searchStepsMultiSelect.data.forEach(option => {
        option.selected = false;  // Mark as unselected
    });
    searchStepsMultiSelect._updateSelected();

    // Clear search_tags
    const searchTagsMultiSelect = new MultiSelect(document.getElementById('search_tags'));
    searchTagsMultiSelect.data.forEach(option => {
        option.selected = false;  // Mark as unselected
    });
    searchTagsMultiSelect._updateSelected();

    // Clear df_mode
    const dfModeMultiSelect = new MultiSelect(document.getElementById('df_mode'));
    dfModeMultiSelect.data.forEach(option => {
        option.selected = false;  // Mark as unselected
    });
    searchTagsMultiSelect._updateSelected();

    form.submit();
}