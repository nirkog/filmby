function toggle_description_expansion(film_element, expanding) {
	const description_container = film_element.querySelector(".film-description");
	const description = film_element.querySelector(".film-description p");

	if (expanding) {
		description_container.style.maxHeight = null;
		description.innerHTML = description.dataset.long_text;
	} else {
		description_container.style.maxHeight = description_container.scrollHeight + "px";
		description.innerHTML = description.dataset.short_text;
		//console.log(description.innerHTML);
	}
}

function on_film_click(e) {
	let current_parent = e.target.parentElement;
	let film_element = undefined;
	while (current_parent != undefined) {
		//console.log(current_parent);
		if (current_parent.classList.contains("film")) {
			film_element = current_parent;
			break;
		}
		current_parent = current_parent.parentElement;
	}

	if (film_element == undefined) {
		return
	}

	const film_index = film_element.dataset.filmIndex;

	const screenings_element = film_element.querySelector(".screenings");
	const expand_icon = film_element.querySelector(".expand i");
	const description = film_element.querySelector(".film-description p");
	if (screenings_element.style.maxHeight) {
		screenings_element.style.maxHeight = null;
		expand_icon.classList.remove("fa-chevron-up");
		expand_icon.classList.add("fa-chevron-down");

		if (g_mobile) {
			toggle_description_expansion(film_element, false);
		} else {
			description.innerHTML = description.dataset.short_text;
		}

		film_element.classList.remove("open");
	} else {
		screenings_element.style.maxHeight = screenings_element.scrollHeight + "px";
		expand_icon.classList.add("fa-chevron-up");
		expand_icon.classList.remove("fa-chevron-down");

		if (g_mobile) {
			toggle_description_expansion(film_element, true);
		} else {
			description.innerHTML = description.dataset.long_text;
		}
		
		film_element.classList.add("open");
	}
}

async function get_films(e) {
	const date_element = document.querySelector("#date_input");
	const town_element = document.querySelector("#town_input");
	const data = await fetch(`/films?date=${date_element.value}&town=Tel Aviv`);
	const element_data = await data.text();
	const films_elemnt = document.querySelector("#films");

	films_elemnt.innerHTML = element_data;

	const screening_link_elements = document.querySelectorAll(".screening-link");
	const film_button_elements = document.querySelectorAll(".film-button");

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
		let CHARACTER_LIMIT = 420;
		if (screen.width < 1300) {
			CHARACTER_LIMIT = 250;
		}
		if (screen.width < 500) {
			CHARACTER_LIMIT = 180;
		}

		let film_description = films[i].querySelector(".film-description p");
		let film_description_text = film_description.innerHTML;
		film_description.dataset.long_text = film_description_text;
		film_description.dataset.short_text = film_description_text;
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
			film_description.dataset.short_text = new_description;
		}

		//if (g_mobile) {
		//	toggle_description_expansion(films[i], false);
		//}
	}

	for (let i = 0; i < screening_link_elements.length; i++) {
		screening_link_elements[i].addEventListener("click", (e) => e.stopPropagation());
	}

	for (let i = 0; i < film_button_elements.length; i++) {
		film_button_elements[i].addEventListener("click", (e) => e.stopPropagation());
	}

	let checked_cinema_names = [];
	const cinema_checkboxes = document.querySelectorAll("#cinema-filters input");
	for (let i = 0; i < cinema_checkboxes.length; i++) {
		if (cinema_checkboxes[i].checked) {
			checked_cinema_names.push(cinema_checkboxes[i].dataset.cinema);
		}
	}

	for (let i = 0; i < films.length; i++) {
		let should_filter_out = true;
		const film = films[i];
		const cinema_tags = film.querySelectorAll(".film-cinema-tag");
		for (let j = 0; j < cinema_tags.length; j++) {
			if (checked_cinema_names.includes(cinema_tags[j].dataset.name)) {
				should_filter_out = false;
				break;
			}
		}

		if (should_filter_out) {
			film.style.display = "none";
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
		//console.log("State is old");
		return;
	} else {
		//console.log("Delta is ", now - state_time);
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

var g_mobile = false;

async function on_load() {
	load_state();
	await load_films();
	enable_or_disable_by_film_button();

	if (screen.width < 600) {
		g_mobile = true;
	}
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
	element.classList.add("autocomplete-item");

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

	enable_or_disable_by_film_button();
}

function enable_or_disable_by_film_button() {
	const input = document.querySelector("#film_search_input");
	const value = input.value;

	let real_name = false;
	for (let i = 0; i < g_films.length; i++) {
		if (value == g_films[i].name) {
			real_name = true;
			break;
		}
	}

	const button = document.querySelector("#by_film_view button");
	if (real_name) {
		button.classList.remove("disabled");
	} else {
		button.classList.add("disabled");
	}
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

		if (item.item != value) {
			add_autocomplete_item(item.item);
		}

		if (item.score == 0) {
			break;
		}
	}

	enable_or_disable_by_film_button();
}

function film_search_focus_handler(e) {
	setTimeout(clear_autocomplete_list, 150);
}

function by_film_button_click_handler(e) {
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

function toggle_search_filters(e) {
	const search_filters = document.querySelector("#search-filters");

	console.log(search_filters.style.maxHeight);
	if (search_filters.style.maxHeight) {
		search_filters.style.maxHeight = null;
	} else {
		search_filters.style.maxHeight = search_filters.scrollHeight + "px";
	}
}

function cinema_filter_checkbox_handler(e) {
	const films = document.querySelectorAll(".film");
	const cinema_checkboxes = document.querySelectorAll("#cinema-filters input");
	let checked_cinema_names = [];
	for (let i = 0; i < cinema_checkboxes.length; i++) {
		if (cinema_checkboxes[i].checked) {
			checked_cinema_names.push(cinema_checkboxes[i].dataset.cinema);
		}
	}

	for (let i = 0; i < films.length; i++) {
		const film = films[i];
		const cinema_tags = film.querySelectorAll(".film-cinema-tag");
		let should_filter_out = true;
		for (let j = 0; j < cinema_tags.length; j++) {
			if (checked_cinema_names.includes(cinema_tags[j].dataset.name)) {
				should_filter_out = false;
				break;
			}
		}

		if (should_filter_out) {
			console.log("FILTERING");
			film.style.display = "none";
		} else{
			film.style.display = null;
		}
	}
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

const by_film_button = document.querySelector("#by_film_view button");
by_film_button.addEventListener("click", by_film_button_click_handler);

const toggle_search_filters_button = document.querySelector("#search-filters-toggle-button");
toggle_search_filters_button.addEventListener("click", toggle_search_filters);

const cinema_filter_checkboxes = document.querySelectorAll("#cinema-filters input");
for (let i = 0; i < cinema_filter_checkboxes.length; i++) {
	cinema_filter_checkboxes[i].addEventListener("change", cinema_filter_checkbox_handler);
}
