var rangeSlider = function () {
    var sliders = document.querySelectorAll('.range-slider');

    sliders.forEach(function (slider) {
      var range = slider.querySelector('.range-slider__range');
      var value = slider.querySelector('.range-slider__value');

      value.innerHTML = range.value;

      range.addEventListener('input', function () {
        value.innerHTML = this.value;
      });
    });
  };

  rangeSlider();