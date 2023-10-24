import { useEffect, useState } from "react";


type ELOProps = {
    value: number;
    name: string;
};
export default function ELO({ value, name }: ELOProps) {

    return (
        <div className="flex flex-col justify-center items-center w-auto ">
            <p className={`text-center p-4 w-full`}>
                {name}
            </p>
            <p className={`text-center p-4 w-full`}>
                {Math.round(value)}
            </p>
        </div>
    );
}