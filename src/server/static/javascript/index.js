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
		window.location = `/film/${film_index}`;
	}
}

async function get_films(e) {
	const date_element = document.querySelector("#date_input");
	const town_element = document.querySelector("#town_input");
	const data = await fetch(`/films?date=${date_element.value}&town=${town_element.value}`);
	const element_data = await data.text();
	const films_elemnt = document.querySelector("#films");

	films_elemnt.innerHTML = element_data;

	films = document.querySelectorAll(".film");
	for (let i = 0; i < films.length; i++) {
		films[i].addEventListener("click", on_film_click);
	}
}

const search_button = document.querySelector("#search_button");
search_button.addEventListener("click", get_films);
