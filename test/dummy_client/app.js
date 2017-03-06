import 'bootstrap';
import 'bootstrap/css/bootstrap.css!';
import $ from 'jquery';
import {AsexorClient, WampAsexorClient} from 'izderadicka/asexor_js_client';
import 'font-awesome';

let startApp = function() {
	  console.log('All loaded');
	  const USER='admin';
	  let count=0,
	      tasksList= new Array(),
	      tasksStatus= new Map(),
				client;

		if (/use-wamp/.test(window.location.search)) {

			client = new WampAsexorClient('ws://127.0.0.1:8880/ws', 'realm1', USER, USER);

		} else {

	  	client = new AsexorClient(window.location.host, USER);
		}
	  client.connect()
	  .then(()=> {
	    console.log('Client ready');

	  })
		.catch((err) => {
			let msg = `Cannot start ASEXOR client ${err}`;
			console.error(msg);
			alert(msg);
		});


	  let task_updated = function (task_id, data) {
	    console.log('Task update', task_id, data);
	    if (tasksStatus.has(task_id)) {
	      let s = tasksStatus.get(task_id);
	      Object.assign(s, data);
	      s.result = data.error? data.error : data.result;
	      show_results()
	    } else {
	      console.log(`ERROR - uknown task ${task_id}`);
	    }
	  }

	  client.subscribe(task_updated);

	  let show_params=function() {
	    let selected=$('#task-type').val();
	    $('#params .form-group').addClass('hidden');
	    $(`#${selected}-params`).removeClass('hidden');
	  }

	  let show_results=function() {
	    var task_id,
	      root=$('<tbody id="results">');
	    for (task_id of tasksList) {
	      var status, row;
	      status= tasksStatus.get(task_id);
	      row=$('<tr>');
	      $('<td>').text(task_id).appendTo(row);
	      $('<td>').text(status.task).appendTo(row);
	      $('<td>').append($('<span>').addClass('status '+status.status).text(status.status)).appendTo(row);
	      $('<td>').text(status.duration || '').appendTo(row);
	      $('<td>').text(status.result).appendTo(row);
	      root.append(row);
	    }
	    $('#results').replaceWith(root)
	  }



	  show_params();
	  $('#task-type').on('change', show_params);
	  $('#run-task').on('click', function (evt) {
	    if (! client.active) {
	      alert('Not connected!');
	      return;
	    }
	    let selected=$('#task-type').val();
	    var args=[], kwargs={};

	    switch (selected) {
	      case 'date':
	        args=[$('#date-format').val()];
	        kwargs={utc:$('#date-utc').prop('checked')};
	        break;
	      case 'sleep':
	        args=[parseInt($('#sleep-time').val())]
	        break;
				case 'invalid':
					args='dummy';
					kwargs = 'usak';
	    };

	    client.exec(selected, args, kwargs).then(
	      function(res) {
	        console.log('Task id is '+ res);
	        tasksList.unshift(res);
	        tasksStatus.set(res, {status:'sent', 'task': selected});
	        show_results();
	      },
	      function(err) {
	        console.error('Task submission error', err);
	        alert(`Failed to submit task ${selected}: ${err}`);
	      }
	    )
	  });

		$(document).on('asexor-client-open', (evt)=> {
			$('#tasks-panel').removeClass('hidden');
			$('#loading-message').addClass('hidden');
		});

		$(document).on('asexor-client-close', (evt)=> {
			$('#tasks-panel').addClass('hidden');
			$('#loading-message').removeClass('hidden');
		});

	};

startApp();
