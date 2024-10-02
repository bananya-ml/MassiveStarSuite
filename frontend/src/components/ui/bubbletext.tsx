import styles from './BubbleText.module.css';

interface BubbleTextProps {
  text: string;
  colorScheme?: 'default' | 'red' | 'orange' | 'indigo' | 'blue';
}

const BubbleText: React.FC<BubbleTextProps> = ({ text, colorScheme = 'default' }) => {
  return (
    <p>
      {text.split("").map((child:string, idx:number) => (
        <span 
          className={`${styles.hoverText} ${styles[`hoverText-${colorScheme}`]}`} 
          key={idx}
        >
          {child}
        </span>
      ))}
    </p>
  );
};

export default BubbleText;