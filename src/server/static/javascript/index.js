function on_film_click(e) {
	let current_parent = e.target.parentElement;
	let film_element = undefined;
	while (current_parent != undefined) {
		console.log(current_parent);
		if (current_parent.classList.contains("film")) {
			film_element = current_parent;
			break;
		}
		current_parent = current_parent.parentElement;
	}

	if (film_element != undefined) {
		const film_index = film_element.dataset.filmIndex;
		//window.open(`/film/${film_index}`, "_blank");
		window.open(`/film/${film_index}`, "_self");
	}
}

async function get_films(e) {
	const date_element = document.querySelector("#date_input");
	const town_element = document.querySelector("#town_input");
	const data = await fetch(`/films?date=${date_element.value}&town=Tel Aviv`);
	const element_data = await data.text();
	const films_elemnt = document.querySelector("#films");

	films_elemnt.innerHTML = element_data;

	let films = document.querySelectorAll(".film");
	for (let i = 0; i < films.length; i++) {
		films[i].addEventListener("click", on_film_click);

		// Sort last |
		let film_details = films[i].querySelector(".film-details");
		if (film_details != undefined) {
			if (film_details.children.length != 0) {
				let last_detail = film_details.children[film_details.children.length - 1];
				last_detail.innerHTML = last_detail.innerHTML.slice(0, -2);
			}
		}

		// Shorten description
		let CHARACTER_LIMIT = 500;
		//console.log(screen.width);
		if (screen.width < 1300) {
			CHARACTER_LIMIT = 250;
		}
		if (screen.width < 500) {
			CHARACTER_LIMIT = 180;
		}

		let film_description = films[i].querySelector(".film-description");
		let film_description_text = film_description.innerHTML;
		if (film_description_text.length > CHARACTER_LIMIT)	{ // TODO: Limit should probably be relative to screen size
			let new_description = film_description_text;
			for (let j = CHARACTER_LIMIT; j < film_description_text.length; j++) {
				if (film_description_text[j] == ' ') {
					new_description = film_description_text.slice(0, j);
					new_description += "...";
					break;
				}
			}
			film_description.innerHTML = new_description;
		}
	}

	let state = {};
	state.films_html = films_elemnt.innerHTML;
	state.date = date_element.value;
	state.time = new Date();

	localStorage.setItem("state", JSON.stringify(state));
}

function load_state() {
	let state = localStorage.getItem("state");
	
	if (null == state) {
		return;
	}

	state = JSON.parse(state);

	const now = new Date();
	const max_delta = 1 * 60 * 60 * 1000;
	const state_time = Date.parse(state.time);
	if (now - state_time > max_delta) {
		console.log("State is old");
		return;
	} else {
		console.log("Delta is ", now - state_time);
	}

	const films_elemnt = document.querySelector("#films");
	films_elemnt.innerHTML = state.films_html;

	let films = document.querySelectorAll(".film");
	for (let i = 0; i < films.length; i++) {
		films[i].addEventListener("click", on_film_click);
	}

	const date_element = document.querySelector("#date_input");
	date_element.value = state.date;
}

async function load_films() {
	const data = await fetch(`/films?town=Tel Aviv&json=True`);
	const json_data = await data.json();

	g_films = json_data;
}

async function on_load() {
	load_state();
	await load_films();
}

function change_view(e) {
	const element = e.target;

	if (element.classList.contains("selected")) {
		return;
	}

	const current_view_button = document.querySelector("#view_menu .selected");
	const current_view = document.querySelector(`#${current_view_button.dataset.viewId}`);
	current_view_button.classList.remove("selected");
	current_view.classList.remove("selected");

	const view_id = element.dataset.viewId;
	const view = document.querySelector(`#${view_id}`);
	element.classList.add("selected");
	view.classList.add("selected");

	if (view_id == "by_film_view") {
		const search_input = document.querySelector("#film_search_input");
		search_input.focus();
	}
}

function add_autocomplete_item(text) {
	const container = document.querySelector("#film_autocomplete_container");
	let element = document.createElement("div");
	element.innerHTML = text;
	element.addEventListener("click", film_search_item_click_handler);
	element.addEventListener("touchstart", film_search_item_click_handler);
	element.classList.add("autocomplete-item");
	console.log(element);

	container.appendChild(element);
}

function clear_autocomplete_list() {
	const container = document.querySelector("#film_autocomplete_container");
	container.innerHTML = "";
}

function set_active_film_autocomplete() {
	if (g_current_film_focus == -1) return;

	const container = document.querySelector("#film_autocomplete_container");
	container.children[g_current_film_focus].classList.add("selected");
}

function remove_active_film_autocomplete() {
	if (g_current_film_focus == -1) return;

	const container = document.querySelector("#film_autocomplete_container");
	container.children[g_current_film_focus].classList.remove("selected");
}

function film_search_keydown_handler(e) {
    if (e.keyCode == 40) {
		remove_active_film_autocomplete();
		g_current_film_focus++;
		set_active_film_autocomplete();
    } else if (e.keyCode == 38) {
		remove_active_film_autocomplete();
		g_current_film_focus--;
		set_active_film_autocomplete();
    } else if (e.keyCode == 13) {
      	e.preventDefault();
      	if (g_current_film_focus > -1) {
			const container = document.querySelector("#film_autocomplete_container");
			container.children[g_current_film_focus].click();
      	}

		const input = document.querySelector("#film_search_input");
		const value = input.value;
		for (let i = 0; i < g_films.length; i++) {
			if (value == g_films[i].name) {
				const index = g_films[i].index;
				window.open(`/film/${index}`, "_self");
				break;
			}
		}
    }
}

function film_search_item_click_handler(e) {
	const element = e.target;
	const input = document.querySelector("#film_search_input");

	clear_autocomplete_list();
	input.value = element.innerHTML;
}

function film_search_input_handler(e) {
	if (g_films == null) {
		return;
	}

	const input = document.querySelector("#film_search_input");
	const value = input.value;

	const options = {
		includeScore: true,
		threshold: 0.5	
	};
	let names = [];
	for (let i = 0; i < g_films.length; i++) {
		let film = g_films[i];
		names.push(film.name);
	}

	const fuse = new Fuse(names, options);
	const result = fuse.search(value);

	g_current_film_focus = -1;
	clear_autocomplete_list();
	for (let i = 0; i < 7; i++) {
		if (result.length <= i) {
			break;
		}

		let item = result[i];	
		add_autocomplete_item(item.item);

		if (item.score == 0) {
			break;
		}
	}
}

function film_search_focus_handler(e) {
	clear_autocomplete_list();
}

const search_button = document.querySelector("#search_button");
search_button.addEventListener("click", get_films);

var g_films = null;
window.addEventListener("load", on_load);

const view_buttons = document.querySelectorAll("#view_menu div");
for (let i = 0; i < view_buttons.length; i++) {
	view_buttons[i].addEventListener("click", change_view);
}

var g_current_film_focus = -1;
const film_search_input = document.querySelector("#film_search_input");
film_search_input.addEventListener("keydown", film_search_keydown_handler);
film_search_input.addEventListener("input", film_search_input_handler);
film_search_input.addEventListener("focus", film_search_focus_handler);
film_search_input.addEventListener("focusout", film_search_focus_handler);
