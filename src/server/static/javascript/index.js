async function get_films(e) {
	const date_element = document.querySelector("#date_input");
	const town_element = document.querySelector("#town_input");
	const data = await fetch(`/films?date=${date_element.value}&town=${town_element.value}`);
	const element_data = await data.text();
	const films_elemnt = document.querySelector("#films");

	films_elemnt.innerHTML = element_data;
}

const search_button = document.querySelector("#search_button");
search_button.addEventListener("click", get_films);

//get_films(null);
