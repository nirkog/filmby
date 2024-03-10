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
	const data = await fetch(`/films?date=${date_element.value}&town=${town_element.value}`);
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

	localStorage.setItem("state", JSON.stringify(state));
}

function load_state() {
	let state = localStorage.getItem("state");
	
	if (null == state) {
		return;
	}

	state = JSON.parse(state);

	const films_elemnt = document.querySelector("#films");
	films_elemnt.innerHTML = state.films_html;

	let films = document.querySelectorAll(".film");
	for (let i = 0; i < films.length; i++) {
		films[i].addEventListener("click", on_film_click);
	}
}

const search_button = document.querySelector("#search_button");
search_button.addEventListener("click", get_films);

window.addEventListener("load", load_state);
