import styled from 'styled-components';

const Card = styled.div`
    background: ${props => props.active ? 'linear-gradient(135deg, #6366f1, #3b82f6)' : 'white'};
    border-radius: 24px;
    padding: 2rem;
    box-shadow: 0 8px 32px rgba(31, 38, 135, 0.15);
    backdrop-filter: blur(4px);
    transition: all 0.3s ease;
    
    &:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 40px rgba(31, 38, 135, 0.25);
    }
`; 