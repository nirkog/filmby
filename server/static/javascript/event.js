function on_load(e) {
	const mobile_event_details_element = document.querySelector(".event-details.mobile");
	if (getComputedStyle(mobile_event_details_element, null).display == "none") {
		const wide_image_element = document.querySelector(".wide-image");
		const tall_image_element = document.querySelector(".tall-image");
		const event_block_element = document.querySelector(".event-block");

		if (wide_image_element.naturalWidth < wide_image_element.naturalHeight) {
			tall_image_element.style.display = "block";
			event_block_element.classList.add("split");
		} else {
			wide_image_element.style.display = "block";
		}
	}

	const event_details_elements = document.querySelectorAll(".event-text");
	for (let i = 0; i < event_details_elements.length; i++) {
		let element = event_details_elements[i];
		if (element.children.length > 1) {
			let last_detail = element.children[element.children.length - 1];
			last_detail.innerHTML = last_detail.innerHTML.slice(0, -2);
		}
	}
}

window.addEventListener("load", on_load);
