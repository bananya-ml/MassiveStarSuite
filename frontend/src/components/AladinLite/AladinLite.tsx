import React, { useEffect, useRef } from 'react';

declare global {
  interface Window {
    A: any;
  }
}

type AladinLiteProps = {
  width?: string;
  height?: string;
  fov?: number;
  onReady?: () => void;
} & (
  | { id: string; ra?: never; dec?: never }
  | { id?: never; ra: string; dec: string }
);

const AladinLite: React.FC<AladinLiteProps> = ({
  width = '700px',
  height = '400px',
  id,
  ra,
  dec,
  fov = 0.1,
  onReady
}) => {
  const aladinRef = useRef<HTMLDivElement>(null);
  const aladinInstance = useRef<any>(null);

  useEffect(() => {
    const script = document.createElement('script');
    script.src = 'https://aladin.cds.unistra.fr/AladinLite/api/v3/latest/aladin.js';
    script.async = true;
    document.body.appendChild(script);

    const initAladin = () => {
      if (aladinRef.current && window.A) {
        window.A.init.then(() => {
          aladinInstance.current = window.A.aladin(aladinRef.current, {
            survey: "P/DSS2/color",
            fov: fov,
            target: id ? `Gaia DR3 ${id}` : `${ra} ${dec}`
          });
          
          // Call onReady when Aladin is initialized
          if (onReady) {
            onReady();
          }
        }).catch((error: Error) => {
          console.error("Failed to initialize Aladin Lite:", error);
        });
      }
    };

    script.onload = initAladin;
    script.onerror = () => console.error("Failed to load Aladin Lite script");

    return () => {
      document.body.removeChild(script);
      if (aladinInstance.current && aladinInstance.current.destroy) {
        aladinInstance.current.destroy();
      }
    };
  }, [id, ra, dec, fov, onReady]);

  useEffect(() => {
    if (aladinInstance.current) {
      if (id) {
        aladinInstance.current.gotoObject(id);
      } else if (ra && dec) {
        aladinInstance.current.gotoRaDec(ra, dec);
        aladinInstance.current.addMarker(ra, dec, {
          color: 'red',
          label: 'Target'
        });
      }
    }
  }, [id, ra, dec]);

  return <div ref={aladinRef} style={{ width, height }} />;
};

export default AladinLite;