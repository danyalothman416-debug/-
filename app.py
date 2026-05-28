products = [
{
"name":"iPhone Cover",
"price":10,
"image":"cover.jpg"
},

{
"name":"PUBG UC",
"price":20,
"image":"uc.jpg"
}
]

for p in products:

    st.markdown(
    '<div class="product-card">',
    unsafe_allow_html=True
    )

    st.image(
    p["image"],
    use_container_width=True
    )

    st.subheader(
    p["name"]
    )

    st.write(
    f'{p["price"]}$'
    )

    st.button(
    "Buy",
    key=p["name"]
    )

    st.markdown(
    "</div>",
    unsafe_allow_html=True
    )
