function selectRun(runName, runId, numberOfRuns){
  for (let i = 1; i <= numberOfRuns; i++) {
      let run = document.getElementById('run-' + i);
      if (i == runId) {
          run.style.backgroundColor = '#e8edf3';
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

function toggleFavouriteRun(runName, favouriteStatus){

  document.getElementById('favourites_run_name_id').value = runName;
  document.getElementById('favourites_run_status_id').value = favouriteStatus;
  document.getElementById('change_favourite').submit();
};

