import { Flex, HStack } from "@chakra-ui/react";
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
    <Flex
      w="100%"
      justifyContent={"center"}
      backgroundColor={"white"}
      p="1"
      position={"fixed"}
      bottom="0"
    >
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
    </Flex>
  );
};

export default PaginationBar;
