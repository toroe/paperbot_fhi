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
    setInterval(fetchPost, 60000);
    
  }, [])
     
  console.log("salam");
     

  return (
    <div>
      <div className="CardItems">
        {cards.map((card) => (
          <CardItem
            title={card.title}
            doi={card.doi}
            authors={card.authors}
            journal={card.journal}
            publication_year={card.publication_year}

          />
        ))}
      </div>
            
            
    </div>
  );
  

}
export default CardItems;
