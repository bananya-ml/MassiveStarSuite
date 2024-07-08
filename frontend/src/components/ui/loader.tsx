import { motion } from "framer-motion";

const BarLoader = ({ height = "1em", width = "0.25em", gap = "0.125em", color = "currentColor" }) => {
  const variants = {
    initial: {
      scaleY: 0.5,
      opacity: 0,
    },
    animate: {
      scaleY: 1,
      opacity: 1,
      transition: {
        repeat: Infinity,
        repeatType: "mirror",
        duration: 1,
        ease: "circIn",
      } as const,
    },
  };

  return (
    <motion.div
      transition={{
        staggerChildren: 0.25,
      }}
      initial="initial"
      animate="animate"
      className="flex"
      style={{ gap }}
    >
      {[...Array(5)].map((_, index) => (
        <motion.div
          key={index}
          variants={variants}
          style={{
            height,
            width,
            background: color,
          }}
        />
      ))}
    </motion.div>
  );
};

export default BarLoader;