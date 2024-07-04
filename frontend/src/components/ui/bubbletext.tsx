import styles from './BubbleText.module.css';

const BubbleText = ({ text, colorScheme = 'default' }) => {
  return (
    <p className="text-lg text-white text-center mt-[50px]">
      {text.split("").map((child, idx) => (
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