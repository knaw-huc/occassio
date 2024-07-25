import {FreeTextFacet, ListFacet, SliderFacet, FacetsParams} from '@knaw-huc/browser-base-react';
import {FACET_URL} from "../misc/config";
import {useEffect, useState} from "react";
import {IFacet, INumberFacet} from "../misc/interfaces.ts";

export default function Facets({registerFacet, unregisterFacet, setFacet, searchValues}: FacetsParams) {

    const [facets, setFacets] = useState([] as IFacet[]);

    useEffect(() => {
        fetch('/api/facets').then((response) => {
            response.json().then(data => {
                setFacets(data);
            });
        })
    }, []);

    const objects = facets.map((facet ) => {
        switch (facet.type) {
            case "text": {
                return <ListFacet
                    registerFacet={registerFacet}
                    key={facet.field}
                    unregisterFacet={unregisterFacet}
                    setFacet={setFacet}
                    name={facet.name}
                    field={facet.field}
                    url={FACET_URL}
                    flex={false}
                    usePost={true}
                    addFilter={true}
                    searchValues={searchValues}/>
            }
            case "number": {
                const numFacet = facet as INumberFacet
                return <SliderFacet
                    key={numFacet.field}
                    registerFacet={registerFacet}
                    unregisterFacet={unregisterFacet}
                    setFacet={setFacet}
                    name={numFacet.name}
                    field={numFacet.field}
                    min={numFacet.min}
                    max={numFacet.max}/>
            }
        }
    })

    return <>
        <FreeTextFacet registerFacet={registerFacet} unregisterFacet={unregisterFacet} setFacet={setFacet}/>
        {objects}
    </>;
}
