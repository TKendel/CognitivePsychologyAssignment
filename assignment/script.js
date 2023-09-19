const synth = window.speechSynthesis;

const inputForm = document.querySelector("form");
const inputTxt = document.getElementById("txt");

const highlight = (text, from, to) => {
  let replacement = highlightBackground(text.slice(from, to));
  return text.substring(0, from) + replacement + text.substring(to);
};
const highlightBackground = (sample) =>
  `<span style="background-color:yellow;">${sample}</span>`;

function speak() {
    let utterance = new SpeechSynthesisUtterance(inputTxt.innerText);
    utterance.addEventListener("boundary", (event) => {
      const { charIndex, charLength } = event;
      inputTxt.innerHTML = highlight(
        inputTxt.innerText,
        charIndex,
        charIndex + charLength
      );
    });
    utterance.volume = 0;
    synth.speak(utterance);
}

inputForm.onsubmit = function (event) {
  event.preventDefault();

  speak();
};
