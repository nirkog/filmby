function on_load(e) {
	const mobile_film_details_element = document.querySelector(".film-details.mobile");
	if (getComputedStyle(mobile_film_details_element, null).display == "none") {
		const wide_image_element = document.querySelector(".wide-image");
		const tall_image_element = document.querySelector(".tall-image");
		const film_block_element = document.querySelector(".film-block");

		if (wide_image_element.naturalWidth < wide_image_element.naturalHeight) {
			tall_image_element.style.display = "block";
			film_block_element.classList.add("split");
		} else {
			wide_image_element.style.display = "block";
		}
	}

	const film_details_elements = document.querySelectorAll(".film-text");
	for (let i = 0; i < film_details_elements.length; i++) {
		console.log("ELEMENT");
		let element = film_details_elements[i];
		if (element.children.length > 1) {
			let last_detail = element.children[element.children.length - 1];
			last_detail.innerHTML = last_detail.innerHTML.slice(0, -2);
		}
	}
}

window.addEventListener("load", on_load);
