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

});


// === FUNCTIONS ===
function selectRun(runName, runId, numberOfRuns){
  for (let i = 1; i <= numberOfRuns; i++) {
      let run = document.getElementById('run-' + i);
      if (i == runId) {
          if (run.style.backgroundColor == 'rgb(232, 237, 243)') {
            run.style.backgroundColor = 'white';
          }
          else {
            run.style.backgroundColor = 'rgb(232, 237, 243)';
            run.style.borderRadius = '10px';
          }
          
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

function toggleFavouriteRun(runName, favouriteStatus){

  document.getElementById('favourites_run_name_id').value = runName;
  document.getElementById('favourites_run_status_id').value = favouriteStatus;
  document.getElementById('change_favourite').submit();
};

