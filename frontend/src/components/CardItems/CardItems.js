import React, { useEffect, useState } from "react";
import CardItem from "../CardItem/CardItem";
import "./CardItems.css";
function CardItems() {
  const [cards, setCards] = useState([]);

  
 

   
  const fetchPost = () => {
    console.log("in fetchPost");
    fetch("http://localhost:5001/update_kiosk/")
      .then((res) => res.json())
      .then((result) => {
        console.log(result);
        setCards(result);
      });
  };
         
  useEffect(() => {
    fetchPost();
    setInterval(fetchPost, 5000);
    
  }, [])
     
  console.log("salam");
     

  return (
    <div>
      <div className="CardItems">
        {cards.map((card) => (
          <CardItem
            title={card.title}
            author={card.body}
            journal={card.journal}
          />
        ))}
      </div>
            
            
    </div>
  );
  

}
export default CardItems;
