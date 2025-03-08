import { HStack } from "@chakra-ui/react";
import {
  PaginationItems,
  PaginationNextTrigger,
  PaginationPrevTrigger,
  PaginationRoot,
} from "@/components/ui/pagination";

interface PaginationBarProps {
  count: number;
  pageSize: number;
  changePage: (page: number) => void;
}

interface PageChangeDetails {
  page: number;
  pageSize: number;
}

const PaginationBar = ({ count, pageSize, changePage }: PaginationBarProps) => {
  return (
    <PaginationRoot
      count={count}
      pageSize={pageSize}
      defaultPage={1}
      variant="solid"
      onPageChange={(details: PageChangeDetails) => changePage(details.page)}
    >
      <HStack>
        <PaginationPrevTrigger />
        <PaginationItems />
        <PaginationNextTrigger />
      </HStack>
    </PaginationRoot>
  );
};

export default PaginationBar;
