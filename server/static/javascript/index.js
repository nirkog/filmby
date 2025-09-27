function toggle_description_expansion(event_element, expanding) {
	const description_container = event_element.querySelector(".event-description");
	const description = event_element.querySelector(".event-description p");

	if (expanding) {
		description_container.style.maxHeight = null;
		description.innerHTML = description.dataset.long_text;
	} else {
		description_container.style.maxHeight = description_container.scrollHeight + "px";
		description.innerHTML = description.dataset.short_text;
		//console.log(description.innerHTML);
	}
}

function on_event_click(e) {
	let current_parent = e.target.parentElement;
	let event_element = undefined;
	while (current_parent != undefined) {
		//console.log(current_parent);
		if (current_parent.classList.contains("event")) {
			event_element = current_parent;
			break;
		}
		current_parent = current_parent.parentElement;
	}

	if (event_element == undefined) {
		return
	}

	const event_index = event_element.dataset.eventIndex;

	const screenings_element = event_element.querySelector(".event-dates");
	const expand_icon = event_element.querySelector(".expand i");
	const description = event_element.querySelector(".event-description p");
	if (screenings_element.style.maxHeight) {
		screenings_element.style.maxHeight = null;
		expand_icon.classList.remove("fa-chevron-up");
		expand_icon.classList.add("fa-chevron-down");

		if (g_mobile) {
			toggle_description_expansion(event_element, false);
		} else {
			description.innerHTML = description.dataset.short_text;
		}

		event_element.classList.remove("open");
	} else {
		screenings_element.style.maxHeight = screenings_element.scrollHeight + "px";
		expand_icon.classList.add("fa-chevron-up");
		expand_icon.classList.remove("fa-chevron-down");

		if (g_mobile) {
			toggle_description_expansion(event_element, true);
		} else {
			description.innerHTML = description.dataset.long_text;
		}
		
		event_element.classList.add("open");
	}
}

async function get_events(e) {
	const date_element = document.querySelector("#date_input");
	const town_element = document.querySelector("#town_input");
	const data = await fetch(`/events?date=${date_element.value}&types=film`);
	const element_data = await data.text();
	const events_elemnt = document.querySelector("#events");

	events_elemnt.innerHTML = element_data;
	console.log("HI");

	const screening_link_elements = document.querySelectorAll(".date-link");
	const event_button_elements = document.querySelectorAll(".event-button");

	let events = document.querySelectorAll(".event");
	for (let i = 0; i < events.length; i++) {
		events[i].addEventListener("click", on_event_click);

		// Sort last |
		let event_details = events[i].querySelector(".event-details");
		if (event_details != undefined) {
			if (event_details.children.length != 0) {
				let last_detail = event_details.children[event_details.children.length - 1];
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

		let event_description = events[i].querySelector(".event-description p");
		let event_description_text = event_description.innerHTML;
		event_description.dataset.long_text = event_description_text;
		event_description.dataset.short_text = event_description_text;
		if (event_description_text.length > CHARACTER_LIMIT)	{ // TODO: Limit should probably be relative to screen size
			let new_description = event_description_text;
			for (let j = CHARACTER_LIMIT; j < event_description_text.length; j++) {
				if (event_description_text[j] == ' ') {
					new_description = event_description_text.slice(0, j);
					new_description += "...";
					break;
				}
			}

			event_description.innerHTML = new_description;
			event_description.dataset.short_text = new_description;
		}

		//if (g_mobile) {
		//	toggle_description_expansion(events[i], false);
		//}
	}

	for (let i = 0; i < screening_link_elements.length; i++) {
		screening_link_elements[i].addEventListener("click", (e) => e.stopPropagation());
	}

	for (let i = 0; i < event_button_elements.length; i++) {
		event_button_elements[i].addEventListener("click", (e) => e.stopPropagation());
	}

	let checked_venue_names = [];
	const venue_checkboxes = document.querySelectorAll("#venue-filters input");
	for (let i = 0; i < venue_checkboxes.length; i++) {
		if (venue_checkboxes[i].checked) {
			checked_venue_names.push(venue_checkboxes[i].dataset.venue);
		}
	}

	for (let i = 0; i < events.length; i++) {
		let should_filter_out = true;
		const event = events[i];
		const venue_tags = event.querySelectorAll(".event-venue-tag");
		for (let j = 0; j < venue_tags.length; j++) {
			if (checked_venue_names.includes(venue_tags[j].dataset.name)) {
				should_filter_out = false;
				break;
			}
		}

		if (should_filter_out) {
			event.style.display = "none";
		}
	}

	let state = {};
	state.events_html = events_elemnt.innerHTML;
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

	const events_elemnt = document.querySelector("#events");
	events_elemnt.innerHTML = state.events_html;

	let events = document.querySelectorAll(".event");
	for (let i = 0; i < events.length; i++) {
		events[i].addEventListener("click", on_event_click);
	}

	const date_element = document.querySelector("#date_input");
	date_element.value = state.date;
}

async function load_events() {
	const data = await fetch(`/events?town=Tel Aviv&json=True`);
	const json_data = await data.json();

	g_events = json_data;
}

var g_mobile = false;

async function on_load() {
	load_state();
	await load_events();
	enable_or_disable_by_event_button();

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

	if (view_id == "by_event_view") {
		const search_input = document.querySelector("#event_search_input");
		search_input.focus();
	}
}

function add_autocomplete_item(text) {
	const container = document.querySelector("#event_autocomplete_container");
	let element = document.createElement("div");
	element.innerHTML = text;
	element.addEventListener("click", event_search_item_click_handler);
	element.classList.add("autocomplete-item");

	container.appendChild(element);
}

function clear_autocomplete_list() {
	const container = document.querySelector("#event_autocomplete_container");
	container.innerHTML = "";
}

function set_active_event_autocomplete() {
	if (g_current_event_focus == -1) return;

	const container = document.querySelector("#event_autocomplete_container");
	container.children[g_current_event_focus].classList.add("selected");
}

function remove_active_event_autocomplete() {
	if (g_current_event_focus == -1) return;

	const container = document.querySelector("#event_autocomplete_container");
	container.children[g_current_event_focus].classList.remove("selected");
}

function event_search_keydown_handler(e) {
    if (e.keyCode == 40) {
		remove_active_event_autocomplete();
		g_current_event_focus++;
		set_active_event_autocomplete();
    } else if (e.keyCode == 38) {
		remove_active_event_autocomplete();
		g_current_event_focus--;
		set_active_event_autocomplete();
    } else if (e.keyCode == 13) {
      	e.preventDefault();
      	if (g_current_event_focus > -1) {
			const container = document.querySelector("#event_autocomplete_container");
			container.children[g_current_event_focus].click();
      	}

		const input = document.querySelector("#event_search_input");
		const value = input.value;

		for (let i = 0; i < g_events.length; i++) {
			if (value == g_events[i].name) {
				const index = g_events[i].index;
				window.open(`/event/${index}`, "_self");
				break;
			}
		}
    }
}

function event_search_item_click_handler(e) {
	const element = e.target;
	const input = document.querySelector("#event_search_input");

	clear_autocomplete_list();
	input.value = element.innerHTML;

	enable_or_disable_by_event_button();
}

function enable_or_disable_by_event_button() {
	const input = document.querySelector("#event_search_input");
	const value = input.value;

	let real_name = false;
	for (let i = 0; i < g_events.length; i++) {
		if (value == g_events[i].name) {
			real_name = true;
			break;
		}
	}

	const button = document.querySelector("#by_event_view button");
	if (real_name) {
		button.classList.remove("disabled");
	} else {
		button.classList.add("disabled");
	}
}

function event_search_input_handler(e) {
	if (g_events == null) {
		return;
	}

	const input = document.querySelector("#event_search_input");
	const value = input.value;

	const options = {
		includeScore: true,
		threshold: 0.5	
	};
	let names = [];
	for (let i = 0; i < g_events.length; i++) {
		let event = g_events[i];
		names.push(event.name);
	}

	const fuse = new Fuse(names, options);
	const result = fuse.search(value);

	g_current_event_focus = -1;
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

	enable_or_disable_by_event_button();
}

function event_search_focus_handler(e) {
	setTimeout(clear_autocomplete_list, 150);
}

function by_event_button_click_handler(e) {
	const input = document.querySelector("#event_search_input");
	const value = input.value;
	for (let i = 0; i < g_events.length; i++) {
		if (value == g_events[i].name) {
			const index = g_events[i].index;
			window.open(`/event/${index}`, "_self");
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

function venue_filter_checkbox_handler(e) {
	const events = document.querySelectorAll(".event");
	const venue_checkboxes = document.querySelectorAll("#venue-filters input");
	let checked_venue_names = [];
	for (let i = 0; i < venue_checkboxes.length; i++) {
		if (venue_checkboxes[i].checked) {
			checked_venue_names.push(venue_checkboxes[i].dataset.venue);
		}
	}

	for (let i = 0; i < events.length; i++) {
		const event = events[i];
		const venue_tags = event.querySelectorAll(".event-venue-tag");
		let should_filter_out = true;
		for (let j = 0; j < venue_tags.length; j++) {
			if (checked_venue_names.includes(venue_tags[j].dataset.name)) {
				should_filter_out = false;
				break;
			}
		}

		if (should_filter_out) {
			console.log("FILTERING");
			event.style.display = "none";
		} else{
			event.style.display = null;
		}
	}
}

const search_button = document.querySelector("#search_button");
search_button.addEventListener("click", get_events);

var g_events = null;
window.addEventListener("load", on_load);

const view_buttons = document.querySelectorAll("#view_menu div");
for (let i = 0; i < view_buttons.length; i++) {
	view_buttons[i].addEventListener("click", change_view);
}

var g_current_event_focus = -1;
const event_search_input = document.querySelector("#event_search_input");
event_search_input.addEventListener("keydown", event_search_keydown_handler);
event_search_input.addEventListener("input", event_search_input_handler);
event_search_input.addEventListener("focus", event_search_focus_handler);
event_search_input.addEventListener("focusout", event_search_focus_handler);

const by_event_button = document.querySelector("#by_event_view button");
by_event_button.addEventListener("click", by_event_button_click_handler);

const toggle_search_filters_button = document.querySelector("#search-filters-toggle-button");
toggle_search_filters_button.addEventListener("click", toggle_search_filters);

const venue_filter_checkboxes = document.querySelectorAll("#venue-filters input");
for (let i = 0; i < venue_filter_checkboxes.length; i++) {
	venue_filter_checkboxes[i].addEventListener("change", venue_filter_checkbox_handler);
}
