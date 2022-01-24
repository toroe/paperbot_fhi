import React from "react";
import "./CardItem.css";

function CardItem({ title, doi, authors, journal, publication_year }) {
  return (
    <div className="Card">
      <div className="CardHeader">
        <h3>{title}</h3>
      </div>

      <div className="CardBody">
        <h5> DOI: {doi}</h5>
        <h5> Author: {authors} </h5>
        <h5> Journal: {journal}</h5>
        <h5> Publication Year: {publication_year}</h5>
      </div>
    </div>
  );
}
export default CardItem;
