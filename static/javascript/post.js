function like(amount, user_id, post_id, liked) {
    const url = "http://127.0.0.1:8080/like";
    const like_label = document.getElementById('like_label');
    const like_button = document.getElementById('like-button');
    var a = parseInt(like_label.textContent.slice(-1));
    var x = like_button.textContent;
    dataa = {user: user_id, post: post_id};
    const resp = fetch(url, {
        method: "POST", // или 'PUT'
        body: JSON.stringify(dataa), // данные могут быть 'строкой' или {объектом}!
        headers: {
            "Content-Type": "application/json",
        }
    });
    if (user_id) {
        if (x == 'Нравится') {
            like_button.textContent = 'Убрать из понравившегося';
            like_label.textContent = 'Лайки: ' + (a+1);
        }
        else {
            like_button.textContent = 'Нравится';
            like_label.textContent = 'Лайки: ' + (a-1);
        }
}
};
