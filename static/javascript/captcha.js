function new_captcha() {
    const characters = 'QWERTYUPLKJHGFDSAZXCVBN23456789';
    let generatedCode = '';
    const url = "http://127.0.0.1:8080/change_captcha_code";

    for (let index = 0; index < 5; index++) {
        generatedCode += characters.charAt(Math.floor(Math.random() * characters.length));
    }
    dataa = {code: generatedCode};
    fetch(url, {
        method: "POST", // или 'PUT'
        body: JSON.stringify(dataa), // данные могут быть 'строкой' или {объектом}!
        headers: {
            "Content-Type": "application/json",
        }
    });
    $("#captcha_photo").html('<img src="/captcha.png/' + generatedCode + '">')
}

    $(document).ready(function() {
        // По клику на картинке обновляем последнюю
        $('#captcha_button').click(function(){
            new_captcha();
        });
    });