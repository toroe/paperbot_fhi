import React from "react";
import "./CardItem.css";

function CardItem({ title, author, journal }) {
  return (
    <div className="Card">
      <div className="CardHeader">
        <h3>{title}</h3>
      </div>

      <div className="CardBody">
        <h5> Author: {author} </h5>
        <h5> Journal:{journal}</h5>
      </div>
    </div>
  );
}
export default CardItem;
