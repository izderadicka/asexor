import 'bootstrap';
import 'bootstrap/css/bootstrap.css!';
import $ from 'jquery';
import { AsexorClient, WampAsexorClient, LongPollAsexorClient } from 'izderadicka/asexor_js_client';
import 'font-awesome';

let startApp = function () {
	console.log('All loaded');
	const USER = 'admin';
	let count = 0,
		tasksList = new Array(),
		tasksStatus = new Map(),
		client,
		sessionId = Math.round(Math.random() * 1000000000);

	let task_updated = function (task_id, data) {
			console.log('Task update', task_id, data);
			if (tasksStatus.has(task_id)) {
				let s = tasksStatus.get(task_id);
				Object.assign(s, data);
				s.result = data.error ? data.error : data.result;
				show_results()
			} else {
				console.log(`ERROR - uknown task ${task_id}`);
			}
		}

	let createClient = function () {
		if (/use-wamp/.test(window.location.search)) {

			client = new WampAsexorClient('ws://127.0.0.1:8880/ws', 'realm1', USER, USER);

		} else if (/use-longpoll/.test(window.location.search)) {

			client = new LongPollAsexorClient('http://localhost:8486', USER);

		} else {
			client = new AsexorClient(window.location.host, USER, sessionId);
		}

		client.subscribe(task_updated);

		return client.connect()
			.then(() => {
				console.log('Client ready');

			})
			.catch((err) => {
				let btn = 	$('#close-btn');
				btn.text('Recreate Client');
				let msg = `Cannot start ASEXOR client ${err}`;
				console.error(msg);
				alert(msg);
			});
	};

	createClient().then( () => $('#close-btn-region').show());

	let show_params = function () {
		let selected = $('#task-type').val();
		$('#params .form-group').addClass('hidden');
		$(`#${selected}-params`).removeClass('hidden');
	}

	let show_results = function () {
		var task_id,
			root = $('<tbody id="results">');
		for (task_id of tasksList) {
			var status, row;
			status = tasksStatus.get(task_id);
			row = $('<tr>');
			$('<td>').text(task_id).appendTo(row);
			$('<td>').text(status.task).appendTo(row);
			$('<td>').append($('<span>').addClass('status ' + status.status).text(status.status)).appendTo(row);
			$('<td>').text(status.duration || '').appendTo(row);
			$('<td>').text(status.result).appendTo(row);
			root.append(row);
		}
		$('#results').replaceWith(root)
	}


	show_params();
	$('#task-type').on('change', show_params);
	$('#run-task').on('click', function (evt) {
		if (!client.active) {
			alert('Not connected!');
			return;
		}
		let selected = $('#task-type').val();
		var args = [], kwargs = {};

		switch (selected) {
			case 'date':
				args = [$('#date-format').val()];
				kwargs = { utc: $('#date-utc').prop('checked') };
				break;
			case 'sleep':
				args = [parseInt($('#sleep-time').val())]
				break;
			case 'invalid':
				args = 'dummy';
				kwargs = 'usak';
		};

		client.exec(selected, args, kwargs).then(
			function (res) {
				console.log('Task id is ' + res);
				tasksList.unshift(res);
				tasksStatus.set(res, { status: 'sent', 'task': selected });
				show_results();
			},
			function (err) {
				console.error('Task submission error', err);
				alert(`Failed to submit task ${selected}: ${err}`);
			}
		)
	});

	$(document).on('asexor-client-open', (evt) => {
		$('#tasks-panel').removeClass('hidden');
		$('#loading-message').addClass('hidden');
		let btn = 	$('#close-btn');
		btn.text('Close Client')
	});

	$(document).on('asexor-client-close', (evt) => {
		$('#tasks-panel').addClass('hidden');
		$('#loading-message').removeClass('hidden');
		let btn = 	$('#close-btn');
		btn.text('Recreate Client');
	});

	$('#close-btn').on('click', (evt) => {
		if (client && client.active) {
		client.close();
		} else {
			createClient()
		}
	})

};

startApp();
